import datetime
import json
import logging
import os
import asyncio
import string
import traceback
from time import sleep

from dotenv import load_dotenv, find_dotenv
from pyrogram import Client

from hft.discovery import record_new_watch, record_new_event, fast_dividend_process
from nlp.lang_models import check_doc_importance, build_news_tags
from nlp.mongo_tools import get_active_channels, update_tg_msg_count, renumerate_channels

import tools.clean_processes
from nlp import client
from tools import compose_td_datetime
from tools.utils import sync_timed, async_timed

load_dotenv(find_dotenv('my.env', True))

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

conf_path = os.path.join(os.environ.get('root_path'), os.environ.get('tg_import_config_path'))

# вроде так норм
sleep_time = 0.33

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


async def import_news(app, channel, limit=None, max_msg_load=1000):
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

    print(f"\nimporting channel {channel['title']}:\n{channel}")

    if channel is None:
        print("Error: channel id is None")
        return

    chat_id = int(channel["tg_id"])
    count = await app.get_chat_history_count(chat_id=chat_id)

    new_msg_count = count - channel['count']
    print(f"{channel['username']} has {new_msg_count} new messages")
    if limit is None:
        limit = min(count - channel['count'], max_msg_load)

    if limit > 0:
        hist = app.get_chat_history(chat_id=chat_id, limit=limit)
        count_num_loaded = 0
        try:
            async for msg in hist:
                count_num_loaded += 1
                print(f"{count_num_loaded}/{limit}")
                res = dict()
                res['channel_title'] = channel.get('title', '')
                res['channel_username'] = channel.get('username', '')
                res['date'] = msg.date
                res['text'] = msg.text or ''
                res['caption'] = msg.caption or ''

                if msg.caption is not None or msg.text is not None:
                    newstext = str(msg.caption) + ' ' + str(msg.text)
                    if res['channel_username'] == 'cbrstocksprivate' and (
                            ('Аномальный объем' in newstext
                             or 'Аномальное изменение цены' in newstext
                             or 'Аномальная лимитка' in newstext
                             or 'Бумаги с повышенной вероятностью' in newstext
                             or 'Аномальный спрос' in newstext
                             or 'Рейтинг акций по чистым ' in newstext)):
                        continue
                    tags = build_news_tags(newstext)
                    res['tags'] = tags

                    if len(tags) > 0:
                        res['parent_tags'] = channel['tags']
                        res['is_important'] = check_doc_importance(res)
                        important_tags = list(set(tags) - {'MOEX'})  # убираем слишком широкие инструменты
                        important_tags = list(filter(lambda n: not n[-1].isdigit(), important_tags))  # убираем фьючерсы
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

                        news_collection.insert_one(res)

        except:
            update_tg_msg_count(channel['username'], count - limit + count_num_loaded - 1)
            return

    if new_msg_count != 0:
        update_tg_msg_count(channel['username'], count)


async def upload_recent_news(app):
    """
    Импортируем все каналы с тегом urgent и 6(non_urgent_channels) non_urgent
    :return:
    """
    conf = json.load(open(conf_path, 'r'))
    conf['last_id'] += 1
    json.dump(conf, open(conf_path, 'w'))

    active_channels = get_active_channels()
    renumerate_channels(is_active=True)

    # после 19-00 начинаем импортировать обычные новости
    non_urgent_channels = conf['non_urgent_channels'] + (1 if datetime.datetime.now().hour >= 19 else 0)

    ids_list = list(
        range((conf['last_id'] - 1) * non_urgent_channels, conf['last_id'] * conf['non_urgent_channels']))

    for channel in active_channels:
        try:
            if 'urgent' in channel['tags'] or (channel['out_id'] in [x % len(active_channels) for x in ids_list]):
                t_start = datetime.datetime.now()
                await import_news(app, channel, limit=None, max_msg_load=10000)
                sleep(sleep_time)
                print(datetime.datetime.now() - t_start)
        except Exception as e:
            print(traceback.format_exc())
            print(f"import_news ERROR: {channel['title']}\n{channel}\n{str(e)}")


start_refresh = compose_td_datetime("0:0:00")
end_refresh = compose_td_datetime("23:30:00")


async def main():
    if not tools.clean_processes.clean_proc("create_tgchanne", os.getpid(), 9999):
        print("something is already running")
        exit(0)

    async with Client("my_account_tgchannels", api_id, api_hash) as app:
        while start_refresh <= datetime.datetime.now() < end_refresh:
            try:
                await upload_recent_news(app)

            except Exception as e:
                print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
