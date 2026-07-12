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
from configs.tg_proxy_config import TG_CLIENT_KWARGS

import logging

logger = logging.getLogger("telegram_send")
logger.setLevel(logging.INFO)

if not logger.handlers:  # чтобы при повторном импорте не дублировать хендлеры
    handler = logging.FileHandler('./logs/telegram_send.log', mode='a', encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s',
        '%Y-%m-%d %H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False  # ВАЖНО: не пускать записи наверх, в общий лог

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

TG_PROXY = {
    "scheme": os.getenv("tg_proxy_scheme", "socks5"),
    "hostname": os.getenv("tg_proxy_host", "127.0.0.1"),
    "port": int(os.getenv("tg_proxy_port", "1088")),
}

USE_PROXY = os.environ.get("use_proxy") == "True"

def tg_client(session_name="my_ccount"):
    return Client(
        session_name,
        api_id,
        api_hash,
        **TG_CLIENT_KWARGS,
    )


async def mtest_send_hello():
    async with tg_client("my_ccount") as app:
        await app.send_message(channel_id_urgent, str("test_login"))

async def mtest_load_chat():
    async with tg_client("my_ccount") as app:
        chat = await app.get_chat(-1001656693918)
        await app.get_chat_history_count(chat_id=-1001656693918)
        chat = json.loads(str(chat))
        chat['is_active'] = 1
        logger.info(chat['id'], chat['title'].strip())
        logger.info(chat.get('username', '').strip(), chat.get('description', '').strip(), chat['members_count'])


async def send_message(msg, urgent=False):
    filename = 'msg_' + datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f") + '.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'msg': msg}, f)


async def send_photo(filepath, urgent=False):
    filename = 'img_' + datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S_%f") + '.json'
    folder = URGENT_PATH if urgent else NORMAL_PATH
    with open(os.path.join(folder, filename), 'w') as f:
        json.dump({'filepath': filepath}, f)


async def send_all_old(min_buffer_size=2000, max_buffer_size=4000):
    async with tg_client("my_ccount") as app:
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
                                next_message = str(filename[:21]) + '\n' + str(data['msg']) + '\n\n'
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


async def send_all(
    min_buffer_size=2000,
    max_buffer_size=4000,
    max_messages_per_cycle=40,
):
    async with tg_client("my_ccount") as app:
        # общий лимит отправок за запуск
        messages_left = max_messages_per_cycle

        # счётчики по каналам
        total_sent_urgent = 0
        total_sent_normal = 0

        async def capped_send_message(stream_id, text):
            nonlocal messages_left, total_sent_urgent, total_sent_normal
            if messages_left <= 0:
                return False
            await app.send_message(stream_id, text)
            messages_left -= 1
            if stream_id == channel_id_urgent:
                total_sent_urgent += 1
            else:
                total_sent_normal += 1
            return True

        async def capped_send_photo(stream_id, filepath):
            nonlocal messages_left, total_sent_urgent, total_sent_normal
            if messages_left <= 0:
                return False
            await app.send_photo(stream_id, filepath)
            messages_left -= 1
            if stream_id == channel_id_urgent:
                total_sent_urgent += 1
            else:
                total_sent_normal += 1
            return True

        # порядок: сначала urgent, потом обычный (как ты и хотел)
        for folder, stream_id in [(URGENT_PATH, channel_id_urgent), (NORMAL_PATH, channel_id)]:
            if messages_left <= 0:
                break

            string_buffer = ""
            files = os.listdir(folder)
            files.sort()

            for filename in files:
                if messages_left <= 0:
                    break

                try:
                    f = os.path.join(folder, filename)
                    logger.debug("Processing file %s", filename)
                    if os.path.isfile(f):
                        with open(f, 'r') as f_read:
                            data = json.load(f_read)

                            # сначала фото (если есть)
                            if 'filepath' in data:
                                ok = await capped_send_photo(stream_id, data['filepath'])
                                if not ok:
                                    break

                            # затем текст
                            if 'msg' in data:
                                next_message = str(filename[:21]) + '\n' + str(data['msg']) + '\n\n'

                                # режем на части, если буфер слишком большой
                                while len(string_buffer) > max_buffer_size and messages_left > 0:
                                    ok = await capped_send_message(stream_id, string_buffer[:max_buffer_size])
                                    if not ok:
                                        break
                                    string_buffer = string_buffer[max_buffer_size:]
                                if messages_left <= 0:
                                    break

                                if len(string_buffer) + len(next_message) > max_buffer_size and len(string_buffer) > 0:
                                    ok = await capped_send_message(stream_id, string_buffer)
                                    if not ok:
                                        break
                                    string_buffer = next_message
                                elif len(string_buffer) + len(next_message) > min_buffer_size:
                                    ok = await capped_send_message(stream_id, string_buffer + next_message)
                                    if not ok:
                                        break
                                    string_buffer = ""
                                else:
                                    string_buffer += next_message

                        logger.debug("Removing %s", f)
                        os.remove(f)

                except Exception as e:
                    logger.exception("Error while processing %s: %s", filename, e)

            # после обхода файлов — дольём оставшийся буфер, пока есть лимит
            while len(string_buffer) > max_buffer_size and messages_left > 0:
                ok = await capped_send_message(stream_id, string_buffer[:max_buffer_size])
                if not ok:
                    break
                string_buffer = string_buffer[max_buffer_size:]

            if len(string_buffer) > 0 and messages_left > 0:
                await capped_send_message(stream_id, string_buffer)

        logger.info(
            "send_all finished: urgent=%d, normal=%d, total=%d (limit=%d)",
            total_sent_urgent,
            total_sent_normal,
            total_sent_urgent + total_sent_normal,
            max_messages_per_cycle,
        )


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
                logger.info(f"Удаляю дубликат: {full_path}")
                os.remove(full_path)
            else:
                # Сохраняем хеш и путь
                seen_hashes[file_hash] = full_path


def get_buffer_file_dt(filename):
    """
    Парсит дату из имени:
    msg_2026_06_15_201234_123456.json
    img_2026_06_15_201234_123456.json
    """
    try:
        name = os.path.basename(filename)

        if not name.endswith(".json"):
            return None

        stem = name[:-5]  # убираем .json
        parts = stem.split("_")

        # msg_YYYY_MM_DD_HHMMSS_micro
        # img_YYYY_MM_DD_HHMMSS_micro
        if len(parts) != 6:
            return None

        if parts[0] not in ("msg", "img"):
            return None

        dt_str = "_".join(parts[1:])
        return datetime.datetime.strptime(dt_str, "%Y_%m_%d_%H%M%S_%f")

    except Exception:
        return None


def keep_last_buffer_files(folder_path, max_files=100):
    files = []

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if not os.path.isfile(full_path):
            continue

        file_dt = get_buffer_file_dt(filename)

        # Нераспознанные имена не трогаем, чтобы случайно не удалить лишнее
        if file_dt is None:
            continue

        files.append((file_dt, full_path))

    if len(files) <= max_files:
        return

    files.sort(key=lambda x: x[0], reverse=True)

    for _, full_path in files[max_files:]:
        logger.info("Removing old buffer file: %s", full_path)
        os.remove(full_path)


if __name__ == "__main__":
    if not tools.clean_processes.clean_proc("telegram_send", os.getpid(), 3):
        logger.info("something is already running")
        exit(0)

    # waiting till monitor will do the job
    sleep(15)

    remove_duplicates_by_content(URGENT_PATH)
    remove_duplicates_by_content(NORMAL_PATH)

    keep_last_buffer_files(URGENT_PATH, max_files=100)
    keep_last_buffer_files(NORMAL_PATH, max_files=100)

    asyncio.run(send_all())

#msg = """hello"""
#asyncio.run(send_message(msg))
