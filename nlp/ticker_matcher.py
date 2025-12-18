# nlp/ticker_matcher.py
from __future__ import annotations
from typing import Iterable, List
import pyahocorasick

# Храним один скомпилированный автомат на процесс
_A: pyahocorasick.Automaton | None = None

def build_automaton(tickers: Iterable[str]) -> None:
    """
    Инициализируй один раз на старте:
      build_automaton(your_tickers_iterable)
    Никаких файлов: ты передаёшь свой источник тикеров сам.
    """
    global _A
    A = pyahocorasick.Automaton(pyahocorasick.STORE_ANY, pyahocorasick.KEYSTRING)

    for t in tickers:
        if not t:
            continue
        u = t.upper()
        # Базовая форма + популярные префиксы
        A.add_word(u, u)
        A.add_word("$" + u, u)
        A.add_word("#" + u, u)

    A.make_automaton()
    _A = A

def extract_tickers(text: str) -> List[str]:
    """
    Быстрая выборка: один проход по тексту (O(n)).
    Требует предварительного build_automaton(...).
    """
    A = _A
    if A is None:
        raise RuntimeError("ticker_matcher not initialized. Call build_automaton(tickers) first.")

    seen = set()
    out: List[str] = []
    # Приводим текст к upper один раз (дешёво)
    for _, val in A.iter(text.upper()):
        if val not in seen:
            seen.add(val)
            out.append(val)
    return out

def is_ready() -> bool:
    return _A is not None
