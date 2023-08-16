import datetime
import json
import os
import asyncio

from dotenv import load_dotenv
from pyrogram import Client
from pymongo import MongoClient

from hft.discovery import record_new_watch, record_new_event
from nlp.lang_models import check_doc_importance, build_news_tags
from nlp.mongo_tools import get_active_channels, update_tg_msg_count, renumerate_channels, remove_news_duplicates

import tools.clean_processes
from refresh import compose_td_datetime


load_dotenv(dotenv_path='./my.env')

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

client = MongoClient()
conf_path = './tg_import_config.json'

# channels = [
#     "AK47pfl"
#     , "cbrstocks"
#     , "smartlabnews"
#     , "ruinvestingcom"
#     , "economika"
#     , "bcsinvestidea"
#     , "finamalert"
#     , "StockNews100"
#     , "renat_vv"
#     , "russianmacro"
#     , "MarketDumki"
#     , "ProfitGate"
#     , "stockexchanger"
#     , "bitkogan"
#     , "SvetaFXTradingBlog"
#     , "yivashchenko"
#     , "RusBafet_VIP"
#     , "dohod"
#     , "brent_crude_oil"
#     , "usertrader3"
#     , "macroresearch"
#     , "Sharqtradein"
#     , "trader_chernyh"
#     , "alfawealth"
#     , "altorafund"
#     , "bondovik"
#     , "buyside", "Brent_Crude_Oil", "xtxixty", "altorafund", "mozgovikresearch", "finpizdec", "markettwits",
#     "alfawealth", "alfa_investments",
#     "bitkogan_hotline", "StockNews100", "usamarke1", "taurenin", "marketsnapshot", -1001656693918]


# channels = ['divonline', 'dohod', 'smfanton', 'divonline', 'usamarke1', 'particular_trader', 'investheroes',
#             'finrangecom', 'zabfin', 'invest_or_lost','PravdaInvest', 'private_investor', 'Tradermoex',
#             'investarter', 'trader_nt','atlant_signals', 'openinvestor', 'arsageranews', 'rynok_znania',
#             'trekinvest','ltrinvestment', 'INVESTR_RU', 'FTMTrends', 'Risk_zakharov', 'if_stocks',
#             'tinkoff_invest_official', 'SberInvestments', 'omyinvestments', 'selfinvestor',
#             'antonchehovanalitk', 'investorylife', 'investokrat', 'truecon', 'scapitalrussia',
#             'rodinfinance', 'warwisdom', 'GBEanalytix', 'truevalue', 'FinamPrem', 'ingosinvest',
#             'alorbroker', 'RSHB_Invest', 'FREEDOMFINANCE', 'open_invest', 'bcs_express',
#             'tinkoff_analytics_official', 'vadya93_official', 'AROMATH', 'romanandreev_trader',
#             'martynovtim', 'invest_budka', 'invest_fynbos', 'razb0rka', 'kuzmlab', 'harmfulinvestor',
#             'meatinvestor'
#
#             ]

channels = ['Alfacapital_ru', 'finam_invest', 'FinamInvestLAB', 'promsvyaz_am',
            'gpb_investments', 'aton1991', 'mkb_investments', 'iticapital_invest'
            ]

async def create_record(chat_id):
    async with Client("my_ccount", api_id, api_hash) as app:
        chat = await app.get_chat(chat_id)
        # count = await app.get_chat_history_count(chat_id=chat_id)
        # print(chat)
        chat = json.loads(str(chat))
        result = dict()
        result["tg_id"] = chat['id']
        result['is_active'] = 1
        result["title"] = chat['title'].strip()
        result["username"] = chat.get('username', '').strip()
        result['description'] = chat.get('description', '').strip()
        result['members_count'] = chat['members_count']
        result['count'] = 0  # count - 100 # to import 100 messages after creation
        # print(result)
        return result


async def create_channels():
    global channels
    channels = set(channels)
    names_collection = client.trading['tg_channels']
    for channel in channels:
        try:
            res = await create_record("@" + channel)
            print(f"Created channel\n{res}")
            names_collection.insert_one(res)
        except Exception as ex:
            print(str(ex))


async def import_news(channel, limit=None, max_msg_load=1000):
    async with Client("my_ccount_tgchannels", api_id, api_hash) as app:
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
            async for msg in hist:
                res = dict()
                res['channel_title'] = channel.get('title', '')
                res['channel_username'] = channel.get('username', '')
                res['date'] = msg.date
                res['text'] = msg.text or ''
                res['caption'] = msg.caption or ''

                if msg.caption is not None or msg.text is not None:
                    tags = build_news_tags(str(msg.caption) + ' ' + str(msg.text))
                    res['tags'] = tags

                    if len(tags) > 0:
                        res['parent_tags'] = channel['tags']

                        res['is_important'] = check_doc_importance(res)
                        important_tags = list(set(tags) - {'MOEX'})  # убираем слишком широкие инструменты
                        important_tags = list(filter(lambda n: not n[-1].isdigit(), important_tags))  # убираем фьючерсы
                        res['important_tags'] = important_tags

                        news_collection.insert_one(res)

                        if len(important_tags) <= 2:
                            try:
                                record_new_watch(res, channel['username'])
                            except Exception as e:
                                print(f"hft record: {channel['username']} \n{res} \n{str(e)}")

                            if res['channel_username'] in ['markettwits','cbrstocks', 'ProfitGateClub', 'divonline']:
                                keyword = ''
                                fulltext = (res['text'] + res['caption']).lower()
                                if "отчет" in fulltext:
                                    keyword = "отчет"
                                elif "дивиденд" in fulltext:
                                    keyword = "дивиденд"
                                elif "собрание" in fulltext:
                                    keyword = "госа"
                                elif "директор" in fulltext:
                                    keyword = "директор"
                                elif "госа" in fulltext:
                                    keyword = "госа"

                                record_new_event(res, channel['username'], keyword)



        if new_msg_count != 0:
            print("updating message count...")
            update_tg_msg_count(channel['username'], count)


async def upload_recent_news():
    conf = json.load(open(conf_path, 'r'))
    conf['last_id'] += 1
    json.dump(conf, open(conf_path, 'w'))

    active_channels = get_active_channels()
    renumerate_channels(is_active=True)

    ids_list = list(range((conf['last_id']-1)*conf['non_urgent_channels'], conf['last_id']*conf['non_urgent_channels']))

    for channel in active_channels:
        try:
            if 'urgent' in channel['tags'] or (channel['out_id'] in [x % len(active_channels) for x in ids_list]):
                await import_news(channel, limit=None, max_msg_load=10000)
        except Exception as e:
            print(f"import_news ERROR: {channel['title']}\n{channel}\n{str(e)}")

start_refresh = compose_td_datetime("0:0:00")
end_refresh = compose_td_datetime("23:30:00")


if __name__ == "__main__":
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("create_tgchanne", os.getpid(), 9999):
        print("something is already running")
        exit(0)

    # nlp.mongotools.remove_news_duplicates()
    while start_refresh <= datetime.datetime.now() < end_refresh:
        try:
            asyncio.run(upload_recent_news())
        except Exception as e:
            print(e)
        print(datetime.datetime.now())
