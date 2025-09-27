import traceback
# sql/get_table.py — добавь рядом с exec_query
from typing import Optional, Any
from sqlalchemy import create_engine, text
import logging
import pandas as pd

engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/test').execution_options(
    autocommit=True)  # insufficient data in "D" message // pool_pre_ping=True
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def exec_script(sql_text: str, params: Optional[tuple | dict] = None) -> None:
    """
    Выполняет МНОГОСТРОЧНЫЙ скрипт (несколько SQL-операторов, разделённых ';')
    в ОДНОЙ транзакции. Без сырых BEGIN/COMMIT в тексте.
    Быстро: один вызов к серверу и один COMMIT.
    """
    # Берём сырой DBAPI-коннект из SQLAlchemy engine
    conn = engine.raw_connection()  # psycopg2 connection
    try:
        # Для транзакции нужно выключить автокоммит у DBAPI-коннекта
        try:
            conn.autocommit = False
        except Exception:
            pass

        cur = conn.cursor()
        try:
            if params is not None:
                # ВАЖНО: для именованных параметров в тексте должны быть %(name)s,
                # для позиционных — %s. (psycopg2-стиль)
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


def df_to_sql(df, table_name, index = False):
    try:
        engine.execute(f"delete from {table_name}")
    except:
        logging.error('clean table failed', traceback.format_exc())
    finally:
        try:
            df.to_sql(table_name, engine, if_exists='append', index=index)
        except:
            logging.error('appending to table failed')
            logging.error(traceback.format_exc())
            df.to_sql(table_name, engine, if_exists='replace', index=index)


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
