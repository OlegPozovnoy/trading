import asyncio
import json
import os

from dotenv import load_dotenv, find_dotenv
from pyrogram import Client

from nlp import client

load_dotenv(find_dotenv('my.env', True))

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']


channels = ['Alfacapital_ru', 'finam_invest', 'FinamInvestLAB', 'promsvyaz_am',
            'gpb_investments', 'aton1991', 'mkb_investments', 'iticapital_invest'
            ]

async def create_record(chat_id):
    """
    setting a new record for insertion to DB
    :param chat_id:
    :return: dict with the new record
    """
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
    """
    вставляем в БД новые каналы для импорта
    :return:
    """
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


if __name__ == "__main__":
    asyncio.run(create_channels())