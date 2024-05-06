import functools
import time
from typing import Callable, Any

import sql.get_table


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} second(s)')
                record_to_db(func, total)

        return wrapped

    return wrapper


def sync_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} second(s)')
                record_to_db(func, total)

        return wrapped
    return wrapper


def record_to_db(func, total):
    func = str(func)
    idx = func.find('at')
    func = func[:idx] if idx > 0 else func
    query = f"""
    INSERT INTO public.func_stats (name, num, avg, min, max, stdev, last)
    VALUES ('{func}', 1, {total}, {total}, {total}, 0, {total})
    ON CONFLICT (name)
    DO UPDATE SET
    num = func_stats.num+1,
    avg = (func_stats.avg*func_stats.num+{total})/(func_stats.num+1),
    min = least(func_stats.min, {total}),
    max = greatest(func_stats.max, {total}),
    stdev = ((func_stats.num-1)*func_stats.stdev + ({total} - func_stats.avg)^2)/func_stats.num,
    last = {total},
    last_invoke = NOW();
    """
    sql.get_table.exec_query(query)
