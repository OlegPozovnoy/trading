import sql.get_table


def get_class_code(secCode):
    query = f"select * from public.futquotes where code='{secCode}'"
    orders = sql.get_table.query_to_list(query)
    return 'TQBR' if len(orders) == 0 else 'SPBFUT'


def get_quotes(classCode, secCode):
    if classCode == 'SPBFUT':
        query = f"""SELECT * FROM public.futquotes where code='{secCode}' LIMIT 1"""
    else:
        query = f"""SELECT * FROM public.secquotes where code='{secCode}' LIMIT 1"""

    return sql.get_table.query_to_list(query)


def get_diff(classCode, secCode):
    if classCode == 'SPBFUT':
        query = f"""SELECT * FROM public.futquotesdiff where code='{secCode}' LIMIT 1"""
    else:
        query = f"""SELECT * FROM public.secquotesdiff where code='{secCode}' LIMIT 1"""

    return sql.get_table.query_to_list(query)


def get_pos(secCode):
    query = f"""SELECT * FROM public.united_pos where code='{secCode}' LIMIT 1"""
    q_res = sql.get_table.query_to_list(query)
    return 0 if len(q_res) == 0 else q_res[0]['pos']
