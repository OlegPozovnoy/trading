import datetime
import logging
import os
import asyncio
import re
import string
import traceback
import time
from typing import Union

from dotenv import load_dotenv, find_dotenv
from pyrogram import Client

import sql.get_table
from hft.discovery import record_new_watch, record_new_event, fast_dividend_process
from nlp.lang_models import check_doc_importance, build_news_tags
from nlp.mongo_tools import get_active_channels, update_tg_msg_count, renumerate_channels

import tools.clean_processes
from nlp import client
from tg_channels import ClientWrapper
from tools import compose_td_datetime
from tools.utils import sync_timed, async_timed
from pyrogram import types, raw, utils

load_dotenv(find_dotenv('my.env', True))

api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

conf_path = os.path.join(os.environ.get('root_path'), os.environ.get('tg_import_config_path'))

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
    global last_session_log_message
    result = []
    try:
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
        result = await utils.parse_messages(wrapper.app, messages, replies=0)

    except Exception as e:
        print(e)
    finally:
        last_log_message = read_last_session_log_message()
        if last_log_message and "Waiting for" in last_log_message:
            timeout_seconds = int(re.search(r'\d+', last_log_message).group())
            last_session_log_message = ""
            wrapper.record_db_performance(timeout_seconds)
        return result


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
            newstext = f"{msg.caption or ''} {msg.text or ''}"
            if res['channel_username'] == 'cbrstocksprivate' and re.search(
                    r'Аномальный объем|Аномальное изменение цены|Аномальная лимитка|Бумаги с повышенной вероятностью|Аномальный спрос|Рейтинг акций по чистым ',
                    newstext):
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


@sync_timed()
def prepare_channels():
    active_channels = get_active_channels()
    renumerate_channels(is_active=True)
    return active_channels


@async_timed()
async def upload_recent_news(wrapper: ClientWrapper):
    """
    Импортируем все каналы с тегом urgent и 6(non_urgent_channels) non_urgent
    :return:
    """
    wrapper.last_id = wrapper.last_id + 1

    # после 19-00 начинаем импортировать обычные новости
    non_urgent_channels = wrapper.non_urgent_channels + (1 if datetime.datetime.now().hour >= 19 else 0)

    ids_list = list(range((wrapper.last_id - 1) * non_urgent_channels, wrapper.last_id * non_urgent_channels))

    for channel in wrapper.channels:
        try:
            if 'urgent' in channel['tags'] or (channel['out_id'] in [x % len(wrapper.channels) for x in ids_list]):
                t_start = datetime.datetime.now()
                logger.info(f"{wrapper.session_name} started {datetime.datetime.now()}")
                await import_news(wrapper, channel, limit=None, max_msg_load=10000)
                logger.info(f"{wrapper.session_name} finished {datetime.datetime.now() - t_start}")
                await asyncio.sleep(wrapper.sleep_time - (time.time() % wrapper.sleep_time))
                logger.info(f"{wrapper.session_name} slept {datetime.datetime.now() - t_start} \n SLEEP_TIME: {wrapper.sleep_time} ")
        except Exception as e:
            print(traceback.format_exc())
            print(f"import_news ERROR: {channel['title']}\n{channel}\n{str(e)}")


start_refresh = compose_td_datetime("0:0:00")
end_refresh = compose_td_datetime("23:30:00")


async def main():
    #if not tools.clean_processes.clean_proc("create_tgchanne", os.getpid(), 9999):
    #    print("something is already running")
    #    exit(0)

    renumerate_channels(is_active=True)

    print("STARTING PRIVATE CLIENT +79261491162")
    async with Client("my_account_tgchannels", os.environ['tg_api_id'], os.environ['tg_api_hash'], ) as app_private:
        print("STARTING PUBLIC CLIENT +79932691162")
        async with Client("my_account_public", os.environ['public_tg_api_id'], os.environ['public_tg_api_hash']) as app_public:

            client_private = ClientWrapper(app_private, api_id, api_hash,
                                           'my_account_tgchannels', is_private=True, sleep_time=0.02)
            client_public = ClientWrapper(app_public, os.environ['public_tg_api_id'],
                                          os.environ['public_tg_api_hash'], 'my_account_public', is_private=False, sleep_time=0.5)
            client_private.print_channels()
            client_public.print_channels()
            while start_refresh <= datetime.datetime.now() < end_refresh:
                try:
                    await asyncio.gather(
                        upload_recent_news(client_private),
                        upload_recent_news(client_public)
                    )
                except Exception as e:
                    print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
