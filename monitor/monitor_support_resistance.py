import pandas as pd

import sql.get_table
from monitor import logger
from tools.utils import sync_timed


@sync_timed()
def update_df_monitor():
    """
    monitor if a sec crossed the support/resistance
    :return:
    """
    check_consistancy_query = """
    select  code, count(*)	FROM public.df_monitor group by code having count(*)>1
    """
    if len(sql.get_table.query_to_df(check_consistancy_query)) > 0:
        sql.get_table.exec_query("delete from public.df_monitor")

    query = """
    WITH current_prices AS (
        SELECT code, (bid + ask) / 2 AS price 
        FROM public.futquotes 
        WHERE bid > 0
        UNION ALL
        SELECT code, (bid + ask) / 2 AS price 
        FROM public.secquotes 
        WHERE bid > 0
    ),
    filtered_levels AS (
        SELECT l.code, l.name AS state, q.price AS price, l.start, 
            l.end, l.std AS new_std, NOW() AS timestamp 
        FROM public.df_all_levels l
        INNER JOIN current_prices q 
        ON l.code = q.code 
        WHERE l.start <= q.price AND l.end > q.price
    )
    SELECT t1.*, t2.state, t2.price, t2.start, t2.end, t2.new_std, t2.timestamp  
    FROM public.df_monitor t1
    FULL JOIN filtered_levels t2 ON t1.code = t2.code
    ORDER BY t2.code DESC;
    """

    df_monitor = sql.get_table.query_to_df(query)
    logger.info("df_monitor imported")
    logger.info(df_monitor.head())

    # переносим not null новое в старое и переносим цену и стд
    colpairs = [('old_price', 'new_price'), ('old_timestamp', 'new_timestamp'),
                ('new_price', 'price'), ('new_timestamp', 'timestamp'),
                ('std', 'new_std'), ('old_state', 'new_state'), ('old_start', 'new_start'), ('old_end', 'new_end')
                ]

    df_monitor = copy_colvals(df_monitor, colpairs)
    logger.info("moved new state to old state")
    logger.info(df_monitor.head())

    # предотврощаем частые апдейты состояния,
    # 1) всегда апдейтим нулл
    # 2) ушли вниз
    # 3) ушли вверх
    df_monitor['to_update'] = (df_monitor['new_state'].isnull()) | \
                              (df_monitor['new_price'] + df_monitor['std'] < df_monitor['old_start']) | \
                              (df_monitor['new_price'] - df_monitor['std'] > df_monitor['old_end'])

    colpairs = [('new_state', 'state'), ('new_start', 'start'), ('new_end', 'end')]

    df_monitor = copy_colvals(df_monitor, colpairs, is_upd_only=True)

    logger.info("updated new and old columns")
    logger.info(df_monitor.head())

    columns = ['index', 'code', 'old_state', 'old_price', 'old_start', 'old_end',
               'new_state', 'new_price', 'new_start', 'new_end', 'std',
               'old_timestamp', 'new_timestamp']

    sql.get_table.df_to_sql(df_monitor[columns], "public.df_monitor")
    logger.info("saved df to df_monitor table")
    return df_monitor[df_monitor['to_update']]


def copy_colvals(df_monitor, colpairs, is_upd_only=False):
    for pairs in colpairs:
        if not is_upd_only:
            df_monitor.loc[df_monitor[pairs[1]].notnull(), pairs[0]] = df_monitor.loc[
                df_monitor[pairs[1]].notnull(), pairs[1]]
        else:
            df_monitor.loc[df_monitor['to_update'] & df_monitor[pairs[1]].notnull(), pairs[0]] = df_monitor.loc[
                df_monitor['to_update'] & df_monitor[pairs[1]].notnull(), pairs[1]]
    return df_monitor


@sync_timed()
def pos_orders_gen():
    query = """
    insert into public.orders_my (state, quantity, remains, comment, stop_loss, take_profit, barrier, max_amount, pause, code, direction, start_time)
    SELECT state, quantity, 0, comment, stop_loss, take_profit, barrier, max_amount, pause, code, direction, start_time	FROM public.trd_pos
    where comment not in (select comment from public.orders_my where end_time is null);
    """
    sql.get_table.exec_query(query)
