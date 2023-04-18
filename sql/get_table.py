from sqlalchemy import create_engine
import logging
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def exec_query(query):
    return engine.execute(query)


def query_to_df(query):
    return pd.DataFrame(exec_query(query))

def query_to_list(query):
    return exec_query(query).mappings().all()


def load_candles():
    return query_to_df("select * from df_all_candles_t")