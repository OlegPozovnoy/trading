import datetime
from time import sleep

from dotenv import load_dotenv, find_dotenv
import asyncio
from pyrogram import Client
import json
import os

import hashlib

import tools.clean_processes
import sql.get_table

load_dotenv(find_dotenv('my.env', True),verbose=True)

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = int(os.environ['tg_channel_id'])
channel_id_urgent = int(os.environ['tg_channel_id_urgent'])

URGENT_PATH = os.path.join(os.environ['root_path'], 'tg_buffer/urgent/')
NORMAL_PATH = os.path.join(os.environ['root_path'], 'tg_buffer/normal/')

engine = sql.get_table.engine

TOKEN = os.environ["INVEST_TOKEN"]

#@pytest.mark.asyncio
async def test_send_hello():
    async with Client("my_ccount", api_id, api_hash) as app:
        await app.send_message(channel_id_urgent, str("test_login"))

#@pytest.mark.asyncio
async def test_load_chat():
    async with Client("my_ccount", api_id, api_hash) as app:
        chat = await app.get_chat(-1001656693918)
        await app.get_chat_history_count(chat_id=-1001656693918)
        chat = json.loads(str(chat))
        chat['is_active'] = 1
        print(chat['id'], chat['title'].strip())
        print(chat.get('username', '').strip(), chat.get('description', '').strip(), chat['members_count'])


async def send_message(msg, urgent=False):
    filename = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f") + '.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'msg': msg}, f)


async def send_photo(filepath, urgent=False):
    filename = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f") + '.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'filepath': filepath}, f)


async def send_all(min_buffer_size=2000, max_buffer_size=4000):
    async with Client("my_ccount", api_id, api_hash) as app:
        for folder, stream_id in [(URGENT_PATH, channel_id_urgent), (NORMAL_PATH, channel_id)]:
            string_buffer = ""
            listdir = os.listdir(folder)
            listdir.sort()
            for filename in os.listdir(folder):
                try:
                    f = os.path.join(folder, filename)
                    print(filename)
                    if os.path.isfile(f):
                        with open(f, 'r') as f_read:
                            data = json.load(f_read)
                            if 'filepath' in data:
                                await app.send_photo(stream_id, data['filepath'])
                            if 'msg' in data:
                                next_message = str(filename[:17]) + '\n' + str(data['msg']) + '\n\n'
                                while len(string_buffer) > max_buffer_size:
                                    await app.send_message(stream_id, string_buffer[:max_buffer_size])
                                    string_buffer = string_buffer[max_buffer_size:]

                                if len(string_buffer) + len(next_message) > max_buffer_size and len(string_buffer) > 0:
                                    await app.send_message(stream_id, string_buffer)
                                    string_buffer = next_message
                                elif len(string_buffer) + len(next_message) > min_buffer_size:
                                    await app.send_message(stream_id, string_buffer + next_message)
                                    string_buffer = ""
                                else:
                                    string_buffer += next_message
                        print(f"removing {f}")
                        os.remove(f)

                except Exception as e:
                    print(str(e))

            while len(string_buffer) > max_buffer_size:
                await app.send_message(stream_id, string_buffer[:max_buffer_size])
                string_buffer = string_buffer[max_buffer_size:]

            if len(string_buffer) > 0:
                await app.send_message(stream_id, string_buffer)


def calculate_file_hash(filepath, chunk_size=1024):
    """Вычисляет хеш SHA256 для файла."""
    hash_algo = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()


def remove_duplicates_by_content(folder_path):
    """Удаляет дубликаты файлов в папке на основе содержимого."""
    seen_hashes = {}  # Словарь для хранения хешей
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            full_path = os.path.join(root, file_name)

            # Вычисляем хеш содержимого файла
            file_hash = calculate_file_hash(full_path)

            if file_hash in seen_hashes:
                # Если хеш уже существует, удаляем файл
                print(f"Удаляю дубликат: {full_path}")
                os.remove(full_path)
            else:
                # Сохраняем хеш и путь
                seen_hashes[file_hash] = full_path


if __name__ == "__main__":
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("telegram_send", os.getpid(), 3):
        print("something is already running")
        exit(0)

    # waiting till monitor will do the job
    sleep(15)

    remove_duplicates_by_content(URGENT_PATH)
    remove_duplicates_by_content(NORMAL_PATH)


    asyncio.run(send_all())

    print(datetime.datetime.now())


#msg = """hello"""
#asyncio.run(send_message(msg))
