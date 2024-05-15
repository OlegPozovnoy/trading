import sql.get_table
from manual_order import execute_manual_order


def get_orders():
    query = """SELECT id, state, quantity, comment, remains, barrier, max_amount, pause,  provider, order_type, barrier_bound
	FROM public.orders_my ORDER BY 1;"""
    return str(sql.get_table.query_to_list(query))


def invert_state(id: int):
    query = f"""UPDATE public.orders_my set state = 1 - state WHERE id = {id}"""
    sql.get_table.exec_query(query)


def place_order(user_data: dict):
    for k, v in user_data.items():
        if v == 'None': user_data[k] = None
    execute_manual_order(user_data['quantity'], user_data['code'], user_data['barrier_up'], user_data['barrier_down'],
                         user_data['order_nums'], user_data['state'], user_data['max_amount'], user_data['pause'])
    return get_orders()
