import asyncio
import datetime
import logging
import os
import re
import string
import time
import traceback
from pathlib import Path
from typing import Union

from dotenv import load_dotenv, find_dotenv
from pyrogram import Client
from pyrogram import raw, utils

import sql.get_table
import tools.clean_processes
from create_tgchannels import ClientWrapper
from create_tgchannels.channel_status_csv import ChannelStatusKVCSV, ChannelInvalidLogHandler
from create_tgchannels.floodwait_csv import FloodWaitCSV, FloodWaitLogHandler
from create_tgchannels.invalid_channels_csv import InvalidChannelsCSV
from create_tgchannels.pyrogram_errors import map_pyrogram_error
from hft.discovery import record_new_watch, record_new_event, fast_dividend_process
from nlp import client
from nlp.lang_models import check_doc_importance, build_news_tags
from nlp.mongo_tools import get_active_channels, update_tg_msg_count, renumerate_channels
from tools import compose_td_datetime
from tools.utils import sync_timed, async_timed

load_dotenv(find_dotenv('my.env', True))

api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

conf_path = os.path.join(os.environ.get('root_path'), os.environ.get('tg_import_config_path'))

USE_PROXY = os.environ.get("use_proxy") == "True"

TG_PROXY = {
    "scheme": os.environ.get("tg_proxy_scheme", "socks5"),
    "hostname": os.environ.get("tg_proxy_host", "127.0.0.1"),
    "port": int(os.environ.get("tg_proxy_port", "1088")),
}

TG_CLIENT_KWARGS = {"proxy": TG_PROXY} if USE_PROXY else {}
# вроде так норм

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

last_session_log_message = None
session_logger = logging.getLogger("pyrogram.session.session")
session_logger.setLevel(logging.INFO)


class SessionLoggingHandler(logging.Handler):
    def emit(self, record):
        global last_session_log_message
        last_session_log_message = self.format(record)


session_logger.addHandler(SessionLoggingHandler())  # Добавляем обработчик для логов pyrogram.session.session


def read_last_session_log_message():
    global last_session_log_message
    return last_session_log_message


@async_timed()
async def get_chat_history_count(wrapper: ClientWrapper, chat_id):
    return await wrapper.app.get_chat_history_count(chat_id=chat_id)


@async_timed()
async def get_chat_history_limit(wrapper: ClientWrapper, chat_id, limit):
    return wrapper.app.get_chat_history(chat_id=chat_id, limit=limit)


@async_timed()
async def get_chat_history_offset2(wrapper: ClientWrapper, chat_id: Union[int, str], offset_id: int, limit):
    messages = await wrapper.app.invoke(
        raw.functions.messages.GetHistory(
            peer=await wrapper.app.resolve_peer(chat_id),
            offset_id=offset_id + 100,
            offset_date=utils.datetime_to_timestamp(utils.zero_datetime()),
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=offset_id,
            hash=0
        ),
        sleep_threshold=60
    )
    wrapper.record_success_calls()
    return await utils.parse_messages(wrapper.app, messages, replies=0)


# --- предкомпилированный антиспам для cbrstocksprivate (как у тебя в if) ---
_CBR_NOISE = re.compile(
    r'(Аномальный объем|Аномальное изменение цены|Аномальная лимитка|Бумаги с повышенной вероятностью|Аномальный '
    r'спрос|Рейтинг акций по чистым)',
    re.IGNORECASE
)


def _msg_text(msg) -> str:
    """Собираем caption+text один раз, без None и лишних пробелов."""
    c = (msg.caption or '').strip()
    t = (msg.text or '').strip()
    if c and t:
        return f"{c} {t}"
    return c or t


def _is_noise_channel(channel_username: str, text: str) -> bool:
    """Выносим правило «пропускаем шум» в одну функцию (быстрый вызов + читаемо)."""
    if channel_username == 'cbrstocksprivate' and _CBR_NOISE.search(text):
        return True
    return False




@sync_timed()
def process_message(msg, channel):
    res = {
        'channel_title': channel.get('title', ''),
        'channel_username': channel.get('username', ''),
        'date': msg.date,
        'text': msg.text or '',
        'caption': msg.caption or '',
        'id': msg.id
    }

    try:
        if msg.caption is not None or msg.text is not None:
            newstext = _msg_text(msg)
            if _is_noise_channel(res['channel_username'], newstext):
                return None
            tags = build_news_tags(newstext)
            res['tags'] = tags

            if len(tags) > 0:
                res['parent_tags'] = channel['tags']

                important_tags = [tag for tag in tags if tag != 'MOEX']
                res['important_tags'] = important_tags

                if len(important_tags) <= 2:
                    if res['channel_username'] in ['cbrstocksprivate', 'ProfitGateClub', 'cbrstock',
                                                   'markettwits']:
                        fulltext = (res['text'] + res['caption']).lower()

                        keyword = ''
                        if "дивиденд" in fulltext:
                            keyword = "дивиденд"
                            if res['channel_username'] == 'cbrstocksprivate':
                                try:
                                    fast_dividend_process(res, fulltext)
                                except:
                                    print(traceback.format_exc())
                        elif "отчет" in fulltext:
                            keyword = "отчет"
                        elif "собрание" in fulltext:
                            keyword = "госа"
                        elif "директор" in fulltext:
                            keyword = "директор"
                        elif "госа" in fulltext:
                            keyword = "госа"

                        fulltext = res['text'] + res['caption']
                        fulltext = "".join([x for x in fulltext if x not in string.punctuation])

                        record_new_event(res, channel['username'], keyword, fulltext)

                    try:
                        record_new_watch(res, channel['username'])
                    except:
                        logger.error(f"hft record: {channel['username']} \n{res} \n{traceback.format_exc()}")

                res['is_important'] = check_doc_importance(res)
                logging.info(f"process_message returned {res}")
                return res
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())


def record_max_id(channel, max_msg_id):
    query = f"""INSERT INTO public.tgchannels_ids(title, chat_id, last_msg_id)
    VALUES ('{channel['username']}',{channel["tg_id"]},{max_msg_id}) ON CONFLICT(chat_id) DO
    UPDATE SET last_msg_id = EXCLUDED.last_msg_id, dt=NOW() 
    """
    if max_msg_id is not None:
        sql.get_table.exec_query(query)


@async_timed()
async def import_news(wrapper: ClientWrapper, channel, limit=None, max_msg_load=1000):
    """
        импортируем новость. расставляем теги, переносим res['parent_tags'] = channel['tags'],
        если есть такие слова ['совет директоров', 'дивиденд', 'суд', 'отчетность', 'СД'] помечаем новость важной
        res['important_tags'] - тут только нормальные теги без фьючей и ММВБ
        если важных тегов меньше 2х - засовываем в order_discovery все данные: news_time, channel_source, min_val, max_val, mean_val, volume
        если канал важный, записываем в event_news поля (code, date_discovery, news_time, channel_source, keyword, msg)
        :param channel:
        :param limit:
        :param max_msg_load:
        :return:
        """
    news_collection = client.trading['news']

    logger.info(f"\n{wrapper.session_name} importing channel {channel['title']}:\n{channel}")

    if channel is None:
        logger.info("Error: channel id is None")
        return

    chat_id = int(channel["tg_id"])
    last_msg = sql.get_table.query_to_list(f"select last_msg_id FROM public.tgchannels_ids where chat_id = {chat_id}")

    max_msg_id = None
    count_num_loaded = 0
    news_to_insert = []  # Список для пакетной вставки новостей

    if len(last_msg) == 0:
        count = await get_chat_history_count(wrapper, chat_id)
        new_msg_count = count - channel['count']
        logger.info(f"{channel['username']} has {new_msg_count} new messages")
        if limit is None:
            limit = min(count - channel['count'], max_msg_load)

        if limit > 0:
            hist = await get_chat_history_limit(wrapper, chat_id, limit)
            try:
                async for msg in hist:
                    max_msg_id = msg.id if max_msg_id is None else max(max_msg_id, msg.id)
                    count_num_loaded += 1
                    logger.info(f"{count_num_loaded}/{limit}")

                    res = process_message(msg, channel)
                    if res is not None:
                        news_to_insert.append(res)

                if news_to_insert:
                    news_collection.insert_many(news_to_insert)
                update_tg_msg_count(channel['username'], count - limit + count_num_loaded - 1)
                record_max_id(channel, max_msg_id)
            except Exception as e:
                logger.error(e)
                raise
    else:
        hist = await get_chat_history_offset2(wrapper, chat_id, offset_id=last_msg[0]['last_msg_id'], limit=max_msg_load)
        try:
            for msg in hist:
                max_msg_id = msg.id if max_msg_id is None else max(max_msg_id, msg.id)
                count_num_loaded += 1
                logger.info(f"{count_num_loaded}/UNKNOWN")
                res = process_message(msg, channel)
                if res is not None:
                    news_to_insert.append(res)

            if news_to_insert:
                news_collection.insert_many(news_to_insert)
            update_tg_msg_count(channel['username'], channel['count'] + count_num_loaded)
            record_max_id(channel, max_msg_id)

        except Exception as e:
            logger.error(e)
            raise


@sync_timed()
def prepare_channels():
    active_channels = get_active_channels()
    renumerate_channels(is_active=True)
    return active_channels


@async_timed()
async def upload_recent_news(wrapper: ClientWrapper):
    cycle_started_at = datetime.datetime.now()

    # 1) “цикл” начинается — очищаем память
    if getattr(wrapper, "invalid_csv", None):
        wrapper.invalid_csv.reset_for_cycle(cycle_started_at)
    if getattr(wrapper, "flood_csv", None):
        wrapper.flood_csv.reset_for_cycle(cycle_started_at)

    try:
        wrapper.last_id = wrapper.last_id + 1

        non_urgent_channels = wrapper.non_urgent_channels + (
            1 if datetime.datetime.now().hour >= 19 or datetime.datetime.now().hour < 9 else 0
        )
        ids_list = list(range((wrapper.last_id - 1) * non_urgent_channels, wrapper.last_id * non_urgent_channels))

        for channel in wrapper.channels:
            try:
                if "urgent" in (channel.get("tags") or []) or (
                        channel.get("out_id") in [x % len(wrapper.channels) for x in ids_list]
                ):
                    t_start = datetime.datetime.now()
                    logger.info(f"{wrapper.session_name} started {datetime.datetime.now()}")
                    await import_news(wrapper, channel, limit=None, max_msg_load=10000)
                    logger.info(f"{wrapper.session_name} finished {datetime.datetime.now() - t_start}")

                    await asyncio.sleep(wrapper.sleep_time - (time.time() % wrapper.sleep_time))
                    logger.info(
                        f"{wrapper.session_name} slept {datetime.datetime.now() - t_start} | SLEEP_TIME={wrapper.sleep_time}"
                    )

            except Exception as e:
                m = map_pyrogram_error(e)

                logger.warning(
                    f"[{wrapper.session_name}] {m['error_code']} | {channel.get('title', '')} | {str(e)}"
                )

                # 2) пишем в память (а не на диск)
                if getattr(wrapper, "invalid_csv", None):
                    wrapper.invalid_csv.add(
                        channel,
                        error_code=m["error_code"],
                        exc=e,
                        action=m.get("action", ""),
                        wait_seconds=m.get("wait_seconds"),
                    )

                if m.get("wait_seconds") and getattr(wrapper, "flood_csv", None):
                    wrapper.flood_csv.add(
                        wait_seconds=int(m["wait_seconds"]),
                        source="exception",
                        message=str(e),
                    )

    finally:
        # 3) КОНЕЦ цикла — один раз перезаписали CSV
        if getattr(wrapper, "invalid_csv", None):
            wrapper.invalid_csv.flush_overwrite()
        if getattr(wrapper, "flood_csv", None):
            wrapper.flood_csv.flush_overwrite()



start_refresh = compose_td_datetime("0:0:00")
end_refresh = compose_td_datetime("23:50:00")


async def main():
    if not tools.clean_processes.clean_proc("create_tgchanne", os.getpid(), 9999):
        print("something is already running")
        raise SystemExit(0)

    renumerate_channels(is_active=True)

    base_dir = Path(__file__).resolve().parent / "create_tgchannels"
    base_dir.mkdir(parents=True, exist_ok=True)

    # ===== status store (KV) в память + один CSV-снапшот на диск =====
    status_store = ChannelStatusKVCSV(base_dir, filename="channels_status.csv")

    # лог-хендлер: ловим твой CHANNEL_INVALID из WARNING:__main__
    main_logger = logging.getLogger(__name__)
    # не дублим при перезапусках из IDE
    for h in list(main_logger.handlers):
        if isinstance(h, ChannelInvalidLogHandler):
            main_logger.removeHandler(h)
    main_logger.addHandler(ChannelInvalidLogHandler(status_store))
    # ===============================================================

    print("STARTING PRIVATE CLIENT +79261491162")
    async with Client(
            "my_account_tgchannels",
            int(os.environ["tg_api_id"]),
            os.environ["tg_api_hash"],
            workdir=str(base_dir),
            **TG_CLIENT_KWARGS,
    ) as app_private:

        print("STARTING PUBLIC CLIENT +79932691162")
        async with Client(
                "my_account_public",
                int(os.environ["public_tg_api_id"]),
                os.environ["public_tg_api_hash"],
                workdir=str(base_dir),
                **TG_CLIENT_KWARGS,
        ) as app_public:

            client_private = ClientWrapper(
                app_private,
                os.environ["tg_api_id"],
                os.environ["tg_api_hash"],
                "my_account_tgchannels",
                is_private=True,
                non_urgent_channels=0,
                sleep_time=0.01,
            )
            client_public = ClientWrapper(
                app_public,
                os.environ["public_tg_api_id"],
                os.environ["public_tg_api_hash"],
                "my_account_public",
                is_private=False,
                non_urgent_channels=1,
                sleep_time=1,
            )

            # ===== CSV/логи в память (снапшот на диск делаем вручную после цикла) =====
            client_private.invalid_csv = InvalidChannelsCSV(base_dir, client_private.session_name)
            client_public.invalid_csv = InvalidChannelsCSV(base_dir, client_public.session_name)

            client_private.flood_csv = FloodWaitCSV(base_dir, client_private.session_name)
            client_public.flood_csv = FloodWaitCSV(base_dir, client_public.session_name)

            pyro_logger = logging.getLogger("pyrogram.session.session")
            for h in list(pyro_logger.handlers):
                if isinstance(h, FloodWaitLogHandler):
                    pyro_logger.removeHandler(h)
            pyro_logger.addHandler(FloodWaitLogHandler(client_private.flood_csv))
            pyro_logger.addHandler(FloodWaitLogHandler(client_public.flood_csv))
            pyro_logger.setLevel(logging.WARNING)
            # ======================================================================

            # ===== общий status store (KV) шарим на оба клиента =====
            client_private.status_store = status_store
            client_public.status_store = status_store

            # заранее подгружаем все каналы в стор (чтобы в CSV сразу были ВСЕ 50 строк)
            status_store.ensure_channels(getattr(client_private, "channels", []), is_private=True)
            status_store.ensure_channels(getattr(client_public, "channels", []), is_private=False)

            # сразу пишем первый снапшот, чтобы даже до первого цикла CSV был полный
            status_store.flush()
            # ======================================================

            client_private.print_channels()
            client_public.print_channels()

            try:
                while start_refresh <= datetime.datetime.now() < end_refresh:
                    try:
                        await asyncio.gather(
                            upload_recent_news(client_private),
                            upload_recent_news(client_public),
                        )

                        # ======= СНАПШОТЫ НА ДИСК (один раз на цикл) =======
                        # чтобы ты открывал CSV и видел цельную таблицу "последнего цикла"
                        status_store.flush()
                        client_private.invalid_csv.flush_overwrite()
                        client_public.invalid_csv.flush_overwrite()
                        client_private.flood_csv.flush_overwrite()
                        client_public.flood_csv.flush_overwrite()
                        # ==================================================

                    except Exception:
                        print(traceback.format_exc())
                        # даже если упали — попробуем зафиксировать то, что успели накопить
                        try:
                            status_store.flush()
                            client_private.invalid_csv.flush_overwrite()
                            client_public.invalid_csv.flush_overwrite()
                            client_private.flood_csv.flush_overwrite()
                            client_public.flood_csv.flush_overwrite()
                        except Exception:
                            pass
            finally:
                # при любом выходе — финальный снапшот
                try:
                    status_store.flush()
                    client_private.invalid_csv.flush_overwrite()
                    client_public.invalid_csv.flush_overwrite()
                    client_private.flood_csv.flush_overwrite()
                    client_public.flood_csv.flush_overwrite()
                except Exception:
                    pass


if __name__ == "__main__":
    asyncio.run(main())