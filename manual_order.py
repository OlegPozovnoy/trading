import logging
import string
import random
import numpy as np
import sql.get_table

logger = logging.getLogger()
logger.setLevel(logging.INFO)
engine = sql.get_table.engine

quantity= 20
code = 'MXZ3'

barrier_up= 307250#13.22#None#309000#12.95#16400
#barrier_up=14
barrier_down= None#29050 #28850 #12#2700
order_nums=1

state = 1
max_amount = 1
pause = 10


if barrier_up is None and barrier_down is None:
    order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
    values ({state}, {int(quantity)}, '{code + '_' + order_code}', 0,null,{max_amount},{pause}, '{code}')
    """
    print(query)
    engine.execute(query)
elif barrier_down is None:
    order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
    values ({state}, {int(quantity)}, '{code + '_' + order_code}', 0,{barrier_up},{max_amount},{pause}, '{code}')
    """
    print(query)
    engine.execute(query)
else:
    barriers = np.linspace(barrier_up, barrier_down, order_nums)
    logger.info(barriers)
    for barrier in barriers:
        order_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code)
        values ({state}, {int(quantity/order_nums)}, '{code+'_'+str(int(barrier))+'_'+order_code}', 0,{barrier},{max_amount},{pause}, '{code}')
        """
        print(query)
        engine.execute(query)

