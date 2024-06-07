import requests
import lxml.html
import re
import tkinter as tk
from tkinter import messagebox
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

url = 'https://www.cbr.ru/press/pr/?file=07062024_133000key.htm'


def fetch_page(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            logging.info('Страница успешно загружена.')
            return r.text
        else:
            logging.info('Страница не найдена (код состояния: %d).', r.status_code)
            return None
    except requests.exceptions.RequestException as e:
        logging.info('Ошибка при запросе страницы: %s.', str(e))
        return None


def extract_first_number_from_h1(html_text):
    try:
        page = lxml.html.document_fromstring(html_text)
        h1_elements = page.cssselect('h1')
        h1_texts = "\n".join([element.text_content() for element in h1_elements])

        # Извлечение чисел с запятой в качестве десятичного разделителя
        numbers_with_comma = re.findall(r'\d+,\d+|\d+', h1_texts)

        if numbers_with_comma:
            # Замена запятой на точку и конвертация в float для первого числа
            first_number = float(numbers_with_comma[0].replace(',', '.'))
            logging.info('Число найдено: %f', first_number)
            return first_number
        else:
            logging.info('Число не найдено в содержимом h1.')
            return None
    except Exception as e:
        logging.info('Ошибка при разборе HTML: %s.', str(e))
        return None


def show_messagebox(message):
    root = tk.Tk()
    root.withdraw()  # Скрытие главного окна
    messagebox.showinfo("Сообщение", message)
    root.destroy()  # Уничтожение главного окна после закрытия messagebox


# Основная логика
while True:
    html_text = fetch_page(url)
    if html_text:
        first_number = extract_first_number_from_h1(html_text)
        if first_number is not None:
            break
    logging.info('Повторная попытка через 60 секунд.')
    time.sleep(60)


if first_number <= 16.5:
    query = "update public.orders_my set state = 1 where id = 179"
elif first_number <= 17.5:
    query = "update public.orders_my set state = 1 where id = 180"
else:
    print("пиздец")

if first_number is not None:
    show_messagebox(float(first_number))
else:
    show_messagebox("Число не найдено")
