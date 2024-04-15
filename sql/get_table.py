import traceback

from sqlalchemy import create_engine
import logging
import pandas as pd

engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/test').execution_options(autocommit=True)  # insufficient data in "D" message // pool_pre_ping=True
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def exec_query(query):
    return engine.execute(query)


def query_to_df(query):
    return pd.DataFrame(exec_query(query))


def query_to_list(query):
    return exec_query(query).mappings().all()


def df_to_sql(df, table_name):
    try:
        engine.execute(f"delete from {table_name}")
    except:
        pass
    finally:
        try:
            df.to_sql(table_name, engine, if_exists='append')
        except:
            print(traceback.format_exc())
            df.to_sql(table_name, engine, if_exists='replace')

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
        result = pd.concat([result,query_to_df(query)], axis=0)
    return result