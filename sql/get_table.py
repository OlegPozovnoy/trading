import logging
# sql/get_table.py — добавь рядом с exec_query
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import text as SAtext

engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432/test?application_name=trading-refresh'
).execution_options(autocommit=True)

logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def exec_script(sql_text: str, params: Optional[tuple | dict] = None) -> None:
    """
    Выполняет МНОГОСТРОЧНЫЙ скрипт (несколько SQL-операторов, разделённых ';')
    в ОДНОЙ транзакции. Без сырых BEGIN/COMMIT в тексте.
    Быстро: один вызов к серверу и один COMMIT.
    """
    # Берём сырой DBAPI-коннект из SQLAlchemy engine (psycopg2 connection)
    conn = engine.raw_connection()
    try:
        # гарантируем транзакционный режим
        try:
            conn.autocommit = False
        except Exception:
            pass

        cur = conn.cursor()
        try:
            if params is not None:
                # psycopg2-плейсхолдеры: %s или %(name)s
                cur.execute(sql_text, params)
            else:
                cur.execute(sql_text)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def exec_query(query):
    return engine.execute(text(query))


def query_to_df(query):
    return pd.DataFrame(exec_query(query))


def query_to_list(query):
    return exec_query(query).mappings().all()


def df_to_sql(df, table_name, index: bool = False):
    """
    Твоя семантика:
      - если таблица уже есть → быстро очистить и добавить (TRUNCATE + append)
      - если таблицы нет / схема не совпала → fallback на replace (создаст заново)
    Плюс ускорения: method='multi', chunksize=2000.
    """
    try:
        # Пытаемся быстрый путь: TRUNCATE + append в одной транзакции
        with engine.begin() as conn:
            try:
                conn.execute(SAtext(f'TRUNCATE TABLE "{table_name}"'))
            except Exception:
                # нет таблицы / нет прав и т.п. — попробуем replace ниже
                pass
            else:
                # удалось TRUNCATE → пробуем батч-вставку
                df.to_sql(
                    table_name,
                    con=conn,
                    if_exists="append",
                    index=index,
                    method="multi",
                    chunksize=2000,
                )
                return  # готово: быстрый путь сработал

        # Если дошли сюда, либо TRUNCATE не прошёл, либо append упал → делаем replace
        df.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=index,
            method="multi",
            chunksize=2000,
        )
    except Exception:
        logging.error("df_to_sql failed for %s", table_name, exc_info=True)


def load_candles():
    return query_to_df("select * from df_all_candles_t")


def load_candles_cutoff(cutofftimes):
    result = pd.DataFrame()
    for cutofftime in cutofftimes:
        query = f"""
        select close, volume, security, class_code, datetime, dt, time from (
        SELECT close, volume, security, class_code, datetime, cast(datetime as date) as dt, datetime::time as time,
        ROW_NUMBER() over(partition by security, cast(datetime as date) order by datetime::time desc) as candle_num
        FROM public.df_all_candles_t 
        where datetime::time<='{str(cutofftime)}'::time
        ) t where candle_num =1
        """
        result = pd.concat([result, query_to_df(query)], axis=0)
    return result


def exec_remote_dblink(query):
    # Формирование запроса с использованием dblink и параметров
    dblink_connection_str = "dbname=test host=10.8.0.3 user=postgres password=postgres"
    dblink_query = f"SELECT dblink_exec('{dblink_connection_str}', $$ {query} $$);"
    # Выполнение запроса через dblink
    return exec_query(dblink_query)
