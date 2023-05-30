import datetime
from dotenv import load_dotenv

import hft.discovery
import nlp.mongo_tools
import nlp.lang_models
from nlp.mongo_tools import get_active_channels
import asyncio
from pyrogram import Client
import json
from pymongo import MongoClient
import os
import tools.clean_processes

load_dotenv(dotenv_path='./my.env')

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

channels = [
    "AK47pfl"
    , "cbrstocks"
    , "smartlabnews"
    , "ruinvestingcom"
    , "economika"
    , "bcsinvestidea"
    , "finamalert"
    , "StockNews100"
    , "renat_vv"
    , "russianmacro"
    , "MarketDumki"
    , "ProfitGate"
    , "stockexchanger"
    , "bitkogan"
    , "SvetaFXTradingBlog"
    , "yivashchenko"
    , "RusBafet_VIP"
    , "dohod"
    , "brent_crude_oil"
    , "usertrader3"
    , "macroresearch"
    , "Sharqtradein"
    , "trader_chernyh"
    , "alfawealth"
    , "altorafund"
    , "bondovik"
    , "buyside", "Brent_Crude_Oil", "xtxixty", "altorafund", "mozgovikresearch", "finpizdec", "markettwits",
    "alfawealth", "alfa_investments",
    "bitkogan_hotline", "StockNews100", "usamarke1", "taurenin", "marketsnapshot", -1001656693918]

#Лимон на чай ? Хомяк активный
channels = ['divonline', 'dohod', 'smfanton', 'divonline', 'usamarke1', 'particular_trader', 'investheroes',
            'finrangecom', 'zabfin', 'invest_or_lost','PravdaInvest', 'private_investor', 'Tradermoex',
            'investarter', 'trader_nt','atlant_signals', 'openinvestor', 'arsageranews', 'rynok_znania',
            'trekinvest','ltrinvestment', 'INVESTR_RU', 'FTMTrends', 'Risk_zakharov', 'if_stocks',
            'tinkoff_invest_official', 'SberInvestments', 'omyinvestments', 'selfinvestor',
            'antonchehovanalitk', 'investorylife', 'investokrat', 'truecon', 'scapitalrussia',
            'rodinfinance', 'warwisdom', 'GBEanalytix', 'truevalue', 'FinamPrem', 'ingosinvest',
            'alorbroker', 'RSHB_Invest', 'FREEDOMFINANCE', 'open_invest', 'bcs_express',
            'tinkoff_analytics_official', 'vadya93_official', 'AROMATH', 'romanandreev_trader',
            'martynovtim', 'invest_budka', 'invest_fynbos', 'razb0rka', 'kuzmlab', 'harmfulinvestor',
            'meatinvestor'

            ]

channels = ['Alfacapital_ru', 'finam_invest', 'FinamInvestLAB', 'promsvyaz_am',
'gpb_investments','aton1991','mkb_investments','iticapital_invest'
]

channels = set(channels)
client = MongoClient()


async def test_func(chat_id):
    async with Client("my_ccount", api_id, api_hash) as app:
        chat = await app.get_chat(chat_id)
        count = await app.get_chat_history_count(chat_id=chat_id)
        # print(chat)
        chat = json.loads(str(chat))
        result = dict()
        result["tg_id"] = chat['id']
        result['is_active'] = 1
        result["title"] = chat['title'].strip()
        result["username"] = chat.get('username', '').strip()
        result['description'] = chat.get('description', '').strip()
        result['members_count'] = chat['members_count']
        result['count'] = 0#count - 100 # to import 100 messages after creation
        # print(result)
        return result


async def create_channels():
    names_collection = client.trading['tg_channels']
    for channel in channels:
        try:
            res = await test_func("@" + channel)
            print(res)
            names_collection.insert_one(res)
        except:
            pass


async def import_news(channel, limit=None, max_msg_load=1000):
    async with Client("my_ccount", api_id, api_hash) as app:
        news_collection = client.trading['news']

        print(f"channel:{channel}")
        if channel is None: return

        chat_id = channel["tg_id"]
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
                #print("message:", msg)
                #print(res)
                if msg.caption is not None or msg.text is not None:
                    tags = nlp.lang_models.build_news_tags(str(msg.caption) + ' ' + str(msg.text))
                    res['tags'] = tags
                    if len(tags)>0:
                        res['is_important'] = nlp.lang_models.check_doc_importance(res)

                        important_tags = list(set(tags) - {'MOEX'})  # убираем слишком широкие инструменты
                        important_tags = list(filter(lambda n: n[-1] != '3', important_tags))
                        if len(important_tags) <= 2:
                            hft.discovery.record_new_watch(res, channel['username'])

                    if len(tags) > 0: #or channel['import_empty']: пока из за большего числа каналов только по теме импорт
                        res['parent_tags'] = channel['tags']
                        news_collection.insert_one(res)

            nlp.mongo_tools.update_tg_msg_count(channel['username'], count)


async def upload_recent_news():
    conf = json.load(open('./tg_import_config.json', 'r'))
    conf['last_id'] += 1
    json.dump(conf, open('./tg_import_config.json', 'w'))

    active_channels = get_active_channels()
    nlp.mongo_tools.renumerate_channels(is_active=True)

    print(conf, len(active_channels))
    ids_list = list(range((conf['last_id']-1)*conf['non_urgent_channels'], conf['last_id']*conf['non_urgent_channels']))

    for channel in active_channels:
        try:
            if 'urgent' in channel['tags'] or (channel['out_id'] in [x % len(active_channels) for x in ids_list]):
                await import_news(channel, limit=None, max_msg_load=10000)
        except Exception as e:
            print(f"Checking {channel['title']}", channel, str(e))


if __name__ == "__main__":
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("create_tgchanne", os.getpid(), 2):
        print("something is already running")
        exit(0)

    asyncio.run(upload_recent_news())
    print(datetime.datetime.now())


#asyncio.run(create_channels())

# asyncio.run(import_news(-1001656693918, limit = 100))
#signal.alarm(590)
#asyncio.run(import_news(-1001075101206, limit=200))
#print(datetime.datetime.now())
#print(get_active_channels())