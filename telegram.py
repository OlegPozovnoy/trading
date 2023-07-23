import datetime
from dotenv import load_dotenv
import asyncio
from pyrogram import Client
import json
import os

import tools.clean_processes
import sql.get_table

load_dotenv(dotenv_path='./my.env')

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = int(os.environ['tg_channel_id'])
channel_id_urgent = int(os.environ['tg_channel_id_urgent'])

URGENT_PATH = './tg_buffer/urgent/'
NORMAL_PATH = './tg_buffer/normal/'


engine = sql.get_table.engine

TOKEN = os.environ["INVEST_TOKEN"]


async def test():
    async with Client("my_ccount", api_id, api_hash) as app:
        await app.send_message(channel_id_urgent, str("test_login"))


async def test_func():
    async with Client("my_ccount", api_id, api_hash) as app:
        chat = await app.get_chat(-1001656693918)
        await app.get_chat_history_count(chat_id=-1001656693918)
        #print(chat)
        #print(chat, type(chat), str(chat))
        chat = json.loads(str(chat))
        chat['is_active'] = 1
        #print(x, type(x))
        print(chat['id'],chat['title'].strip(), chat.get('username','').strip(), chat.get('description','').strip(), chat['members_count'])


async def main():
    async with Client("my_ccount", api_id, api_hash) as app:
        count = await app.get_chat_history_count(chat_id=-1001656693918)
        print("msg_count:", count)
        # async for msg in hist:
        hist=[]
        async for msg in hist:
            print(msg.date, msg.text, msg.caption, type(msg.date))
            await app.send_message(channel_id, str(msg.date) + " " + str(msg.caption) + " " + str(msg.text))

        # await app.log_out()


async def send_message(msg, urgent=False):
    filename = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f")+'.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'msg': msg}, f)


async def send_photo(filepath, urgent=False):
    filename = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f")+'.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'filepath': filepath}, f)



async def send_all():
    async with Client("my_ccount", api_id, api_hash) as app:
        for dir, stream_id in [(URGENT_PATH, channel_id_urgent), (NORMAL_PATH, channel_id)]:
            listdir = os.listdir(dir)
            listdir.sort()
            for filename in os.listdir(dir):
                try:
                    f = os.path.join(dir, filename)
                    print(filename)
                    if os.path.isfile(f):
                        with open(f, 'r') as f_read:
                            data = json.load(f_read)
                            if 'filepath' in data:
                                    await app.send_photo(stream_id, data['filepath'])
                            if 'msg' in data:
                                    await app.send_message(stream_id, str(filename[:17])+ '\n'+ str(data['msg']))
                        os.remove(f)
                except:
                    pass


if __name__ == "__main__":
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("telegram", os.getpid(), 3):
        print("something is already running")
        exit(0)
    asyncio.run(send_all())
    print(datetime.datetime.now())


#asyncio.run(test())
#asyncio.run(send_message("Hello"))
