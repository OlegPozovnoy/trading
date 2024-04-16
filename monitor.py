import asyncio
import os
import traceback

import pandas as pd

import sql.get_table
import telegram
import tools.clean_processes
from monitor import send_df, logger, send_all_graph
from monitor.monitor_gains_volumes import monitor_gains_main, format_volumes
from monitor.monitor_imports import monitor_import
from monitor.monitor_support_resistance import update_df_monitor

pd.set_option('display.max_columns', None)
def cut_trailing(df, col_list):
    for col in col_list:
        df[col] = df[col].astype(float).astype(str).replace(r'0+$', '', regex=True)
    return df


def normalize_money(df, col_list):
    for col in col_list:
        df[col] = df[col] / 1000
        df[col] = df[col].astype(int)
    return df


if __name__ == '__main__':
    logger.info("monitor started: ")

    try:
        monitor_import(check_sec=False, check_fut=True, check_tinkoff=True)
    except Exception as e:
        asyncio.run(telegram.send_message(f'monitor_import failed: {traceback.print_exc()}', True))

    if not tools.clean_processes.clean_proc("monitor", os.getpid(), 4):
        logger.info("something is already running")
        exit(0)

    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    logger.info("urgent_list:" + str("('" + "'.'".join(urgent_list)) + "')")

    try:
        df_monitor = update_df_monitor()
        logger.debug(f"states updated: {df_monitor.code.drop_duplicates()}")
    except Exception as e:
        asyncio.run(telegram.send_message(f'update_df_monitor failed: {traceback.format_exc()}', True))

    try:
        send_df(normalize_money(sql.get_table.query_to_df(
            "select money_prev, money, pos_current, pos_plan, pnl, pnl_prev from public.pos_money"),
            ['money_prev', 'money', 'pos_current', 'pos_plan', 'pnl', 'pnl_prev']), True)
    except Exception as e:
        asyncio.run(telegram.send_message(f'normalize_money failed: {traceback.format_exc()}', True))

    volume_tf = pd.DataFrame()
    try:
        intresting_gains, df_volumes = monitor_gains_main(urgent_list)
        logger.info("df_volumes")
        logger.info(df_volumes.head())
        volume_tf = format_volumes(df_volumes[df_volumes['timeframe'] == 'days'])
        logger.info(volume_tf.head())
        volume_tf = volume_tf[['security', 'std', 'inc', 'beta', 'base_inc', 'r2']]
    except Exception as e:
        asyncio.run(telegram.send_message(f'monitor_gains_main: {traceback.format_exc()}', True))

    try:
        query = """
        select code, pos, pnl, price_balance, volume from public.united_pos 
        union
        select 'ZTOTAL' , 0 ,sum(pnl), 0, sum(volume) from public.united_pos
        order by 1 asc;
        """
        pos_df = (sql.get_table.query_to_df(query)
                  .merge(volume_tf, how='left', left_on='code', right_on='security'))

        send_df(cut_trailing(
            normalize_money(pos_df,['pnl', 'volume']),
            ['pnl', 'price_balance', 'volume']), True)
        send_all_graph(intresting_gains, urgent_list)
    except Exception as e:
        asyncio.run(telegram.send_message(f'send_pnl/send_all_graph: {traceback.format_exc()}', True))

    logger.info("monitor: ended")
