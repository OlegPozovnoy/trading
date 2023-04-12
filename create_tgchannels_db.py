import datetime
import time

import hft.discovery
import nlp.mongo_tools
import nlp.lang_models
from nlp.mongo_tools import get_active_channels

key = "1337743768:AAFPfYpYqkbRkii5wZbH5PKtKrACKyifJAY"

api_id = "1961024"
api_hash = "6d5112fa19798f8e832a13587bfc4fe3"

import asyncio
from pyrogram import Client
import json
from pymongo import MongoClient

channel_id = -667947767
channel_id_urgent = -876592585

channels = [
    "AK47pfl"
    , "cbrstocks"
    , "smartlabnews"
    , "ruinvestingcom"
    , "economika"
    , "bcsinvestidea"
    , "finamalert"
    , "StockNews100"
    , "bbbreaking"
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
        result['count'] = count
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


async def import_news(username, limit=None, max_msg_load=1000):
    async with Client("my_ccount", api_id, api_hash) as app:
        names_collection = client.trading['tg_channels']
        news_collection = client.trading['news']

        channel = names_collection.find_one({"username": username})

        print(f"channel:{channel}")
        if channel is None: return

        chat_id = channel["tg_id"]
        count = await app.get_chat_history_count(chat_id=chat_id)

        new_msg_count = count - channel['count']
        print(f"{username} has {new_msg_count} new messages")
        if limit is None:
            limit = min(count - channel['count'], max_msg_load)

        if limit > 0:
            hist = app.get_chat_history(chat_id=chat_id, limit=limit)
            async for msg in hist:
                res = dict()
                res['channel_title'] = channel.get('title', '')
                res['channel_username'] = channel.get('username', '')
                res['date'] = msg.date
                res['text'] = msg.text
                res['caption'] = msg.caption
                print("message:", msg)
                print(res)
                if msg.caption is not None or msg.text is not None:
                    tags = nlp.lang_models.build_news_tags(str(msg.caption) + ' ' + str(msg.text))
                    res['tags'] = tags
                    if len(tags)>0: hft.discovery.record_new_watch(tags, res['date'], username)
                    news_collection.insert_one(res)

            nlp.mongo_tools.update_tg_msg_count(username, count)



async def upload_recent_news():
    active_channels = get_active_channels()
    print(active_channels)
    for channel in active_channels:
        await import_news(channel['username'], limit=None, max_msg_load=1000)

# asyncio.run(create_channels())

# asyncio.run(import_news(-1001656693918, limit = 100))

#asyncio.run(import_news(-1001075101206, limit=200))
asyncio.run(upload_recent_news())
print(datetime.datetime.now())
#print(get_active_channels())