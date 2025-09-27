# bench_llm.py
import time, statistics as st
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm.llm_gpt import get_gpt_text

SYSTEM = (
  "Классифицируй трейдинг-сообщение. Ответь строго одним словом: BUY, SELL или INFO. "
  "Без пояснений, без знаков препинания."
)

# Примеры — расширяй своими реальными сообщениями
DATA = [
  ("Покупаю Сбер, добираю позицию по 265", "BUY"),
  ("Фиксирую прибыль по Газпрому, выхожу", "SELL"),
  ("Yandex ждет отчёт завтра, наблюдаем", "INFO"),
  ("Не покупаю TCSG, слишком высокий риск", "INFO"),  # отрицание
  ("Thinking to add long on LKOH", "BUY"),
  ("Closing long on MGNT, тейк достигнут", "SELL"),
]

def classify(text: str) -> str:
    # просим один короткий ответ; messages — чтобы убрать лишние токены
    msg = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]
    out = get_gpt_text(
        text="",                    # игнорируется, т.к. передаём messages
        messages=msg,
        temperature=0,
        max_tokens=4,               # достаточно 1–4 токенов
    ).strip().upper()
    # нормализуем мусор
    if "BUY" in out: return "BUY"
    if "SELL" in out: return "SELL"
    return "INFO"

def run_bench(workers=1, repeat=1):
    # WARMUP
    classify("Тестовое сообщение для прогрева")

    times = []
    gold, pred = [], []
    tasks = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for _ in range(repeat):
            for text, label in DATA:
                tasks.append(ex.submit(_once, text, label))
        for fut in as_completed(tasks):
            t_ms, y, yhat = fut.result()
            times.append(t_ms)
            gold.append(y); pred.append(yhat)

    acc = sum(1 for y, yhat in zip(gold, pred) if y==yhat) / len(gold)
    print(f"n={len(times)}, acc={acc:.3f}, p50={st.median(times):.1f}ms, "
          f"p95={percentile(times, 95):.1f}ms, min={min(times):.1f}ms, max={max(times):.1f}ms")

def _once(text, label):
    t0 = time.perf_counter()
    yhat = classify(text)
    dt = (time.perf_counter()-t0)*1000
    return dt, label, yhat

def percentile(a, p):
    if not a: return 0.0
    s = sorted(a); k = max(0, min(len(s)-1, int(round((p/100)*(len(s)-1)))))
    return s[k]

if __name__ == "__main__":
    # сначала последовательно (workers=1), потом можно 2–4 потока (осторожно с лимитами)
    run_bench(workers=1, repeat=3)
