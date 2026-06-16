import re
import html
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs

URLS = [
    "https://cbr.ru/press/pr/?file=14022025_133000key.htm",
    "https://cbr.ru/press/pr/?file=21032025_133000key.htm",
    "https://cbr.ru/press/pr/?file=25042025_133000key.htm",
    "https://cbr.ru/press/pr/?file=06062025_133000key.htm",
    "https://cbr.ru/press/pr/?file=25072025_133000key.htm",
    "https://cbr.ru/press/pr/?file=12092025_133000key.htm",
    "https://cbr.ru/press/pr/?file=24102025_133000key.htm",
    "https://cbr.ru/press/pr/?file=19122025_133000key.htm",

    # 13.02.2026 — заседание ЦБ по ключевой ставке
    "https://cbr.ru/press/pr/?file=13022026_133000key.htm",
    # 20.03.2026 — заседание ЦБ по ключевой ставке
    "https://cbr.ru/press/pr/?file=20032026_133000key.htm",
    # 24.04.2026 — заседание ЦБ по ключевой ставке
    "https://cbr.ru/press/pr/?file=24042026_133000key.htm",
    # 19.06.2026 — заседание ЦБ по ключевой ставке
    "https://cbr.ru/press/pr/?file=19062026_133000key.htm",
]

# Регулярка под формулировку ЦБ (первое предложение с "принял решение ... ключевую ставку ... до/на уровне XX% годовых")
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

def parse_meeting_date(url: str) -> datetime | None:
    """Достаем дату из параметра file=DDMMYYYY_..."""
    try:
        qs = parse_qs(urlparse(url).query)
        file_val = qs.get("file", [""])[0]
        ddmmyyyy = file_val[:8]
        return datetime.strptime(ddmmyyyy, "%d%m%Y")
    except Exception:
        return None

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

def main(urls: list[str]) -> dict:
    # На всякий случай сортируем по дате из file=...
    urls_sorted = sorted(urls, key=lambda u: parse_meeting_date(u) or datetime.max)

    prev_rate = None
    results = {}

    for url in urls_sorted:
        try:
            status, page = fetch(url)
            rate = extract_rate_from_html(page)

            if rate is None:
                results[url] = f"не удалось извлечь ставку (HTTP {status})"
                continue

            if prev_rate is not None and abs(rate - prev_rate) < 1e-9:
                results[url] = prev_rate
            else:
                results[url] = rate
                prev_rate = rate

        except requests.HTTPError as e:
            code = getattr(e.response, "status_code", None)
            results[url] = f"не открылось (HTTP {code})"
        except requests.RequestException as e:
            results[url] = f"не открылось ({type(e).__name__}: {e})"
        except Exception as e:
            results[url] = f"ошибка парсинга ({type(e).__name__}: {e})"

    return results

if __name__ == "__main__":
    out = main(URLS)
    for url, val in out.items():
        print(f"{url} -> {val}")
