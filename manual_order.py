import logging
import string
import random
import numpy as np
import sql.get_table
from tools.utils import sync_timed

logger = logging.getLogger()
logger.setLevel(logging.INFO)
engine = sql.get_table.engine

#schema = 'mos'
if 'schema' not in locals():
    schema = 'public'


quantity = -1
code = 'SRM4'

barrier_up = None  # 28250#307250#13.22#None#309000#12.95#16400
barrier_down = None  # 29050 #28850 #12#2700
order_nums = 1

state = 0
max_amount = 1
pause = 1

print(schema)


def execute_manual_order(quantity, code, barrier_up, barrier_down, order_nums, state, max_amount, pause):
    global schema
    if barrier_up is None and barrier_down is None:
        order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
            values ({state}, {int(quantity)}, '{code + '_' + order_code}', 0,null,{max_amount},{pause}, '{code}')
            """
        print(query)
        if schema == 'public':
            engine.execute(query)
        else:
            sql.get_table.exec_remote_dblink(query)
    elif barrier_down is None:
        order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
            values ({state}, {int(quantity)}, '{code + '_' + order_code}', 0,{barrier_up},{max_amount},{pause}, '{code}')
            """

        print(query)
        if schema == 'public':
            engine.execute(query)
        else:
            sql.get_table.exec_remote_dblink(query)
    else:
        barriers = np.linspace(barrier_up, barrier_down, order_nums)
        logger.info(barriers)
        for barrier in barriers:
            order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
            values ({state}, {int(quantity / order_nums)}, '{code + '_' + str(int(barrier)) + '_' + order_code}', 0,{barrier},{max_amount},{pause}, '{code}')
            """
            print(query)
            if schema == 'public':
                engine.execute(query)
            else:
                sql.get_table.exec_remote_dblink(query)


@sync_timed()
def get_volume_params(asset):
    query = f"""
    SELECT *
	FROM public.df_volumes where security = '{asset}'  
	and (now()::time - tm::time) between interval '-4 hours' and interval '-4 hours 1 minutes'
    """
    res = sql.get_table.query_to_list(query)
    print(res[0])
    query = f"""
    select * from df_all_candles_t
    left join df_volumes on
    df_volumes.tm::time = df_all_candles_t.datetime::time and df_volumes.security = df_all_candles_t.security
    where df_all_candles_t.security = '{asset}' 
    and datetime = (select max(datetime) from df_all_candles_t where security='{asset}')
    """
    res = sql.get_table.query_to_list(query)
    print(res[0])


if __name__ == '__main__':
    execute_manual_order(quantity, code, barrier_up, barrier_down, order_nums, state, max_amount, pause)
