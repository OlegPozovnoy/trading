import time
import logging
import sql.get_table
from datetime import datetime, time as dt_time
import re
import requests
import html

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

url = "https://cbr.ru/press/pr/?file=19062026_133000key.htm"
#url = 'https://cbr.ru/press/pr/?file=24102025_133000key.htm'

RATE_RE = re.compile(
    r"(?is)принял\s+решение[^.]{0,450}?ключевую\s+ставку[^.]{0,250}?"
    r"(?:до|на\s+уровне)\s*([0-9]{1,2}(?:[.,][0-9]{1,2})?)\s*%?\s*годов"
)

# Запасной вариант (если вдруг первое предложение сверстано нестандартно)
RATE_RE_FALLBACK = re.compile(
    r"(?is)\bключевую\s+ставку\b.{0,300}?(?:до|на\s+уровне)\s*([0-9]{1,2}(?:[.,][0-9]{1,2})?)\s*%?\s*годов"
)

def strip_tags(s: str) -> str:
    """Грубое удаление HTML-тегов + нормализация пробелов."""
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\xa0", " ").replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch(url: str, timeout=20) -> tuple[int, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.status_code, r.text



def extract_rate_from_html(page_html: str) -> float | None:
    """Извлекаем ставку из HTML (сначала пытаемся по тексту, потом по 'сырым' данным)."""
    raw = html.unescape(page_html)
    text = strip_tags(raw)

    m = RATE_RE.search(text) or RATE_RE_FALLBACK.search(text)
    if not m:
        # Иногда помогает поиск по "сырому" HTML (если слова разорваны тегами)
        m = RATE_RE.search(raw) or RATE_RE_FALLBACK.search(raw)

    if not m:
        return None

    num = m.group(1).replace(",", ".")
    return float(num)



# Основная логика
while True:
    try:
        status, page = fetch(url)
        if page:
            rate = extract_rate_from_html(page)
            if rate is not None:
                break
            else:
                print(f"не удалось извлечь ставку (HTTP {status})")
        # Получаем текущее время
        now = datetime.now().time()
        print(now)
        # Задаем пороговое время
        threshold0 = dt_time(13, 29, 55)
        threshold1 = dt_time(13, 29, 40)
        threshold2 = dt_time(13, 28, 00)
        threshold_out = dt_time(13, 35, 00)

        # Сравнение
        if now > threshold_out:
            sleeptimer = 100000000
        elif now > threshold0:
            sleeptimer = 0.1
        elif now > threshold1:
            sleeptimer = 0.5
        elif now > threshold2:
            sleeptimer = 3
        else:
            sleeptimer = 30
        logging.info(f'Повторная попытка через {sleeptimer} секунд.')
        time.sleep(sleeptimer)

    except requests.HTTPError as e:
        code = getattr(e.response, "status_code", None)
        print(f"не открылось (HTTP {code})")
    except requests.RequestException as e:
        print(f"не открылось ({type(e).__name__}: {e})")
    except Exception as e:
        print(f"ошибка парсинга ({type(e).__name__}: {e})")


if rate > 14:
    query = "update public.orders_my set state = 1 where id = 53"
    sql.get_table.exec_query(query)
    query = "update public.orders_my set state = 1 where id = 54"
    sql.get_table.exec_query(query)
    query = "update public.orders_my set state = 1 where id = 55"
    sql.get_table.exec_query(query)
    query = "update public.orders_my set state = 1 where id = 56"
    sql.get_table.exec_query(query)
    #query = "update public.orders_my set state = 1 where id = 180"
else:
    pass
    #print("пиздец")

print(rate)
if rate is not None:
    print(float(rate))
    #show_messagebox(float(first_number))
else:
    print("Число не найдено")
    #show_messagebox("Число не найдено")
