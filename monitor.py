import os
import sql.get_table
import tools.clean_processes
from monitor import send_df, logger, send_all_graph
from monitor.monitor_gains_volumes import monitor_gains_main
from monitor.monitor_imports import monitor_import
from monitor.monitor_support_resistance import update_df_monitor


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
    monitor_import(check_sec=False, check_fut=True, check_tinkoff=True)

    if not tools.clean_processes.clean_proc("monitor", os.getpid(), 4):
        logger.info("something is already running")
        exit(0)

    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    logger.info("urgent_list:" + str(urgent_list))

    df_monitor = update_df_monitor()
    logger.debug(f"states updated: {df_monitor.code.drop_duplicates()}")

    monitor_gains_main(urgent_list)
    intresting_gains = monitor_gains_main(urgent_list)

    send_df(cut_trailing(
        normalize_money(
            sql.get_table.query_to_df("select code, pos, pnl, price_balance, volume from public.united_pos"),
            ['pnl', 'volume']),
        ['pnl', 'price_balance', 'volume']), True)

    send_df(normalize_money(sql.get_table.query_to_df(
        "select money_prev, money, pos_current, pos_plan, pnl, pnl_prev from public.pos_money"),
        ['money_prev', 'money', 'pos_current', 'pos_plan', 'pnl', 'pnl_prev']), True)

    send_all_graph(intresting_gains)
    logger.info("monitor: ended")


