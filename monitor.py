import asyncio
import os
import traceback

import pandas as pd

import sql.get_table
import telegram_send
import tools.clean_processes
from monitor import send_df, logger, send_all_graph, calculate_ratio
from monitor.monitor_gains_volumes import monitor_gains_main, format_volumes
from monitor.monitor_imports import monitor_import
from monitor.monitor_support_resistance import update_df_monitor
from test import get_orderbook

pd.set_option('display.max_columns', None)


def cut_trailing(df, col_list):
    for col in col_list:
        df[col] = df[col].astype(float).astype(str).replace(r'0+$', '', regex=True).str[:7]
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
        asyncio.run(telegram_send.send_message(f'monitor_import failed: {traceback.format_exc()}', True))

    if not tools.clean_processes.clean_proc("monitor", os.getpid(), 4):
        logger.info("something is already running")
        exit(0)

    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    logger.info("urgent_list:" + str("('" + "'.'".join(urgent_list)) + "')")

    try:
        df_monitor = update_df_monitor()
        df_monitor = df_monitor[df_monitor['code'].isin(urgent_list)]
        send_df(df_monitor[['code', 'old_state', 'new_state']], True)
        logger.debug(f"states updated: {df_monitor.code.drop_duplicates()}")
    except Exception as e:
        asyncio.run(telegram_send.send_message(f'update_df_monitor failed: {traceback.format_exc()}', True))

    try:
        send_df(normalize_money(sql.get_table.query_to_df(
            "select money_prev as moneyt1, money, pos_current as pos, pos_plan as plan, pnl, pnl_prev as pnlt1 from public.pos_money"),
            ['moneyt1', 'money', 'pos', 'plan', 'pnl', 'pnlt1']), True)
    except Exception as e:
        asyncio.run(telegram_send.send_message(f'normalize_money failed: {traceback.format_exc()}', True))

    volume_tf = pd.DataFrame()
    try:
        intresting_gains, df_volumes = monitor_gains_main(urgent_list)
        plita_list = get_orderbook(urgent_list)
        intresting_gains = pd.concat([intresting_gains, df_monitor['code'], plita_list]).drop_duplicates()
        volume_tf = format_volumes(df_volumes[df_volumes['timeframe'] == 'days'])
        volume_tf = volume_tf[['security', 'std', 'inc', 'beta', 'base_inc', 'r2']]
    except Exception as e:
        asyncio.run(telegram_send.send_message(f'monitor_gains_main: {traceback.format_exc()}', True))

    try:
        query = "select * from public.trd_mypos"
        pos_df = (sql.get_table.query_to_df(query)
                  .merge(volume_tf, how='left', left_on='code', right_on='security'))

        for col in ['mktprice', 'lower', 'upper','bid','ask']:
            pos_df[col] = pos_df[col].astype(float).round(3)

        pos_df['l_plit'] = calculate_ratio(pos_df) * 100
        pos_df['l_plit'] = pos_df['l_plit'].astype(float).round(2).astype(str)

        pos_df = cut_trailing(
            normalize_money(pos_df, ['pnl', 'volume']),
            ['pnl', 'mktprice', 'volume', 'lower', 'upper', 'bid', 'bid_qty', 'ask', 'ask_qty'])

        send_df(pos_df[['code', 'pos', 'pnl', 'mktprice', 'volume', 'actnum', 'levels', 'inc', 'std']], True)
        send_df(pos_df[['code', 'levels', 'lower', 'upper',  'bid_qty','bid', 'mktprice', 'ask', 'ask_qty', 'l_plit']], True)
        send_df(pos_df[['code', 'inc', 'beta', 'base_inc', 'r2', 'std']], False)

        logger.info(f"intresting_gains: {intresting_gains}")
        if len(intresting_gains) > 0: send_all_graph(intresting_gains, urgent_list)
    except Exception as e:
        asyncio.run(telegram_send.send_message(f'send_pnl/send_all_graph: {traceback.format_exc()}', True))

    logger.info("monitor: ended")
