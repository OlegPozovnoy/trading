import requests
import lxml.html
import re
#import tkinter as tk
#from tkinter import messagebox
import time
import logging
import sql.get_table
from datetime import datetime, time as dt_time

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

url = 'https://www.cbr.ru/press/pr/?file=06062025_133000key.htm'


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
    pass
    #root = tk.Tk()
    #root.withdraw()  # Скрытие главного окна
    #messagebox.showinfo("Сообщение", message)
    #root.destroy()  # Уничтожение главного окна после закрытия messagebox


# Основная логика
while True:
    html_text = fetch_page(url)
    if html_text:
        first_number = extract_first_number_from_h1(html_text)
        if first_number is not None:
            break
    # Получаем текущее время
    now = datetime.now().time()
    print(now)
    # Задаем пороговое время
    threshold1 = dt_time(13, 29, 40)

    # Задаем пороговое время
    threshold2 = dt_time(13, 28, 00)

    # Сравнение
    if now > threshold1:
        sleeptimer = 1
    elif now > threshold2:
        sleeptimer = 3
    else:
        sleeptimer = 30
    logging.info(f'Повторная попытка через {sleeptimer} секунд.')
    time.sleep(sleeptimer)


if first_number > 20.5 or abs(first_number) < 0.5 :
    query = "update public.orders_my set state = 1 where id = 28"
    sql.get_table.exec_query(query)
    query = "update public.orders_my set state = 1 where id = 29"
    sql.get_table.exec_query(query)
elif first_number <= 17.5:
    pass
    #query = "update public.orders_my set state = 1 where id = 180"
else:
    pass
    #print("пиздец")

print(first_number)
if first_number is not None:
    print(float(first_number))
    #show_messagebox(float(first_number))
else:
    print("Число не найдено")
    #show_messagebox("Число не найдено")
