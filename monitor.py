import datetime
import os

import pandas as pd

import telegram
import asyncio
import matplotlib.pyplot as plt
import sql.get_table
import config.sql_queries
from datetime import datetime, timedelta
import tools.clean_processes
from tools.utils import sync_timed

import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(handler)

engine = sql.get_table.engine
loaded_candles = None


@sync_timed()
def load_candles():
    global loaded_candles
    if loaded_candles is None:
        logger.info("load candles: getting df_all_candles_t candles from database")
        loaded_candles = sql.get_table.query_to_df(
            f"select * from df_all_candles_t  where datetime >  (CURRENT_DATE-14) order by datetime asc")
    else:
        logger.info("load candles: getting df_all_candles_t candles from cache")
    return loaded_candles


@sync_timed()
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
def update_tables(filtered=False):
    df_monitor = []

    try:
        df_monitor = pd.DataFrame(engine.execute(
            "select code, old_state, old_price, old_start, old_end, new_state, new_price, new_start, new_end, std, "
            "old_timestamp, new_timestamp from public.df_monitor"))
    except Exception as e:
        logger.error(str(e))

    check_consistancy_query = """select  code, count(*)	FROM public.df_monitor
        group by code having count(*)>1"""

    if len(df_monitor) == 0 or len(pd.DataFrame(engine.execute(check_consistancy_query))) > 0:
        sql.get_table.exec_query("delete from public.df_monitor")
        df_monitor = pd.DataFrame([], columns=['code', 'old_state', 'old_price', 'old_start', 'old_end', 'new_state',
                                               'new_price', 'new_start', 'new_end', 'std', 'old_timestamp',
                                               'new_timestamp'])
        df_monitor.to_sql('df_monitor', engine, if_exists='append')

    columns = df_monitor.columns

    query = config.sql_queries.monitor["filtered_query"] if filtered else config.sql_queries.monitor[
        "non_filtered_query"]
    df_new = pd.DataFrame(engine.execute(query))
    logger.debug("df_new (new data):\n" + df_new.head().to_string())

    df_monitor = df_monitor.merge(df_new, how='outer', on='code')
    logger.info("df_monitor: moving new state to old state\n" + df_monitor.head().to_string())

    # переносим not null новое в старое и переносим цену и стд
    colpairs = [('old_price', 'new_price'), ('old_state', 'new_state'), ('old_start', 'new_start'),
                ('old_end', 'new_end'), ('old_timestamp', 'new_timestamp'), ('new_price', 'price'), ('std', 'new_std'),
                ('new_timestamp', 'timestamp')]

    df_monitor = copy_colvals(df_monitor, colpairs)
    logger.info("step2: df_monitor\n" + df_monitor.head().to_string())

    df_monitor['to_update'] = df_monitor['new_state'].isnull() | (
            df_monitor['new_price'] + df_monitor['std'] < df_monitor['old_start']) | \
                              (df_monitor['new_price'] - df_monitor['std'] > df_monitor['old_end'])

    colpairs = [('new_state', 'state'), ('new_start', 'start'), ('new_end', 'end')]

    df_monitor = copy_colvals(df_monitor, colpairs, is_upd_only=True)
    logger.info("step3: df_monitor full (updated states)\n" + df_monitor.head().to_string())
    logger.info("step3: df_monitor[to_update]==True - filtered\n" + df_monitor[df_monitor['to_update']].to_string())

    sql.get_table.exec_query("delete from public.df_monitor")
    df_monitor[columns].to_sql('df_monitor', engine, if_exists='append')
    logger.info("df_monitor finished")
    return df_monitor[df_monitor['to_update']]


@sync_timed()
def prepare_images(df_monitor_code_series):
    days_to_subtract = 7
    logger.info(f"preparing images {df_monitor_code_series}")
    df = sql.get_table.query_to_df(
        f"select * from df_all_candles_t  where datetime > NOW() -  interval '{days_to_subtract + 1} days' order by datetime asc")

    df['t'] = pd.to_datetime(df['datetime'])
    start_date = datetime.today() - timedelta(days=days_to_subtract)
    start_date = start_date.replace(tzinfo=df['t'][0].tzinfo)
    df = df[df['t'] > start_date]

    query = f"select * from public.df_levels"
    df_eq = pd.DataFrame(engine.execute(query))

    query = f"select * from public.df_all_volumes"
    df_volumes = pd.DataFrame(engine.execute(query))

    for sec in df_monitor_code_series:
        df_ = df[df['security'] == sec]
        df_eq_ = df_eq[df_eq['sec'] == sec]
        df_volumes_ = df_volumes[df_volumes['code'] == sec]
        plot_price_volume(df_, df_eq_, df_volumes_,
                          title=f"{sec} {datetime.now()}", filename=f"{sec}")
    logger.info("Monitor: graphs updated")


@sync_timed()
def plot_price_volume(df, df_eq, df_volumes, title="title", filename="fig"):
    df = df.sort_values('datetime')
    fig, ax_left = plt.subplots()
    plt.xticks(rotation=90)
    fig.set_figheight(9)
    fig.set_figwidth(16)
    fig.align_ylabels()

    ax_right = ax_left.twiny()
    if len(df_volumes) > 0:
        ax_right.plot(df_volumes['volume'], df_volumes['price'], color='green', linestyle='dashed')
        ax_right.axis(xmax=max(df_volumes['volume']) * 3)

    ax_left.locator_params(axis='x', nbins=25)
    ax_left.locator_params(axis='y', nbins=20)
    ax_left.plot(df['close'])

    # бьем вертикальными линиями по дням
    res = []
    df['datetime'] = df['datetime'].astype(str)
    prev_row = None
    for idx, row in df.iterrows():
        if row['datetime'][:10] != prev_row:
            res.append((idx, row['datetime'][:10]))
        prev_row = row['datetime'][:10]

    for idx, dt in res:
        ax_left.axvline(x=idx, color='g', linestyle='-', label=dt)

    plt.title(title)
    for _, row in df_eq.iterrows():  # np.array([t[0] for t in peaks]):
        ax_left.axhline(y=row['price'], color='r', linestyle='-')
        if row['min_start']:
            # ax_left.axhline(y=row['min_start'], color='g', linestyle='-')
            # ax_left.axhline(y=row['max_start'], color='g', linestyle='-')
            # ax_left.axhline(y=row['end'], color='m', linestyle='-')
            # if (row['down']) != "0":
            #    ax_left.axhline(y=row['sl'], color='k', linestyle='-')
            pass

    logger.info("Monitor: Saving file")
    plt.savefig(f'./level_images/{filename}.png', dpi=50)


@sync_timed()
def get_gains(min_lag=10, threshold=0.5):
    # возвращаем то чот выросло нв трешхолд процентов за минлаг минут
    df = load_candles()
    df['cdate'] = pd.to_datetime(df['datetime'])  # , format="%d.%m.%Y %H:%M")

    start_date = datetime.now() - timedelta(minutes=min_lag)
    start_date = start_date.replace(tzinfo=df['cdate'][0].tzinfo)

    logger.info(f"get_gains:df {start_date} + {df['cdate'][0].tzinfo} + \n{df.head()}")
    df_start = df[df['cdate'] < start_date]
    df_end = df

    df_start = df_start.sort_values(['security', 'cdate']).groupby(['security']).tail(1)
    df_end = df_end.sort_values(['security', 'cdate']).groupby(['security']).tail(1)

    df_res = df_end.merge(df_start, how='inner', on='security')[
        ['security', 'class_code_x', 'close_x', 'close_y', 'cdate_x', 'cdate_y']]
    df_res['inc'] = (df_res['close_x'] / df_res['close_y'] - 1) * 100
    logger.info(f"get_gains:df_res \n {df_res.head()}")

    df_fut = df_res[df_res['class_code_x'] == 'SPBFUT'].sort_values('inc').reset_index()
    df_eq = df_res[df_res['class_code_x'] != 'SPBFUT'].sort_values('inc').reset_index()
    df_inc = pd.concat([df_eq.head(5), df_eq.tail(5), df_fut.head(5), df_fut.tail(5)])[
        ['security', 'inc', 'close_x', 'cdate_x']] \
        .sort_values('inc').reset_index(drop=True)

    df_inc['cdate_x'] = df_inc['cdate_x'].apply(lambda x: x.strftime("%H:%M"))
    df_inc['inc'] = df_inc['inc'].round(2)
    logger.info(f"full df inc\n {df_inc}" )
    return df_res[(df_res['inc'] >= threshold) | (df_res['inc'] <= -threshold)], df_inc


@sync_timed()
def send_gains(df_gains, urgent_list=None):
    logger.debug("df_info:", df_inc.to_string(justify='left', index=False))
    if urgent_list is None:
        urgent_list = []
    for idx, row in df_gains.iterrows():
        #before = round(row['close_y'], 4)
        #after = round(row['close_x'], 4)
        #inc = round(row['inc'], 2)

        #msg = f'{row["security"]} {inc}: {before} -> {after}  {row["cdate_x"]}'
        is_urgent = (row["security"] in urgent_list)
        #asyncio.run(telegram.send_message(msg, is_urgent))
        asyncio.run(telegram.send_photo(f'./level_images/{row["security"]}.png', is_urgent))


@sync_timed()
def get_abnormal_volumes(include_daily=True, minutes_lookback=10, days_lookback=14):
    def get_volumes(minutes_lookback=minutes_lookback, days_lookback=days_lookback):
        start_time = (datetime.now() - timedelta(minutes=minutes_lookback)).time()
        end_time = (datetime.now()).time()

        start_date = (datetime.now() - timedelta(days=days_lookback)).date()
        end_date = (datetime.now()).date()

        df = load_candles()
        df['cdate'] = pd.to_datetime(df['datetime'])
        df['ctime'] = df['cdate'].dt.time
        df['cdt'] = df['cdate'].dt.date

        # считаем mean std volumes предыдущегго и текущего периодов
        df_prev = df.loc[(df['cdate'].dt.time > start_time) & (df['cdate'].dt.time <= end_time) &
                         (df['cdate'].dt.date >= start_date) & (df['cdate'].dt.date < end_date)] \
            .groupby([df['cdate'].dt.date, 'security']).sum('volume').reset_index() \
            .groupby('security').agg(volume_mean=('volume', 'mean'), volume_std=('volume', 'std')).reset_index()

        df_now = df.loc[(df['cdate'].dt.time > start_time) & (df['cdate'].dt.time <= end_time) &
                        (df['cdate'].dt.date == end_date)] \
            .groupby([df['cdate'].dt.date, 'security']).sum('volume').reset_index()[['security', 'volume']]

        df_analys = df_prev.merge(df_now, how='inner', on='security')
        df_analys['std'] = (df_analys['volume'] - df_analys['volume_mean']) / df_analys['volume_std']
        df_analys['end_time'] = end_time

        return df_analys[df_analys['std'] >= 3].sort_values('std', ascending=False)

    df_minutes = get_volumes()
    df_minutes['timeframe'] = 'mins'

    # 540 это -9 часов, чтобы это сработало в 9 утра
    df_daily = get_volumes(minutes_lookback=540) if include_daily else pd.DataFrame()
    df_daily['timeframe'] = 'days'

    return pd.concat([df_minutes, df_daily], axis=0).reset_index()


@sync_timed()
def send_abnormal_volumes(df_volumes, urgent_list=None):
    if urgent_list is None:
        urgent_list = []
    for idx, row in df_volumes.iterrows():
        # msg = f'{row["security"]} {row["timeframe"]} {round(row["std"], 1)}: \
        #    vol:{int(row["volume"])} avg:{int(row["volume_mean"])} std:{int(row["volume_std"])} {row["end_time"]}'
        # logger.debug(msg)
        is_urgent = (row["security"] in urgent_list)

        #    asyncio.run(telegram.send_message(msg, is_urgent))

        if row["timeframe"] == 'mins':
            asyncio.run(telegram.send_photo(f'./level_images/{row["security"]}.png', is_urgent))


@sync_timed()
def get_bollinger():
    query = """SELECT code, quote, round(bollinger::numeric,2) as bollinger, count, 
    round(up::numeric,2) as up, round(down::numeric,2) as down
    FROM public.quote_bollinger 
    where (class_code = 'SPBFUT' and abs(bollinger) > 1.7) 
    or abs(bollinger) > 2 
    or code in (select code from public.pos_bollinger);"""
    return pd.DataFrame(sql.get_table.exec_query(query))


@sync_timed()
def send_df(df, is_urgent=False):
    if len(df) > 0:
        asyncio.run(telegram.send_message(df.to_string(justify='left', index=False), is_urgent))


@sync_timed()
def check_quotes_import():
    check_quotes_import_refresh()
    check_quotes_import_emptytable()
    check_quotes_import_5min()
    check_quotes_import_money()


@sync_timed()
def check_quotes_import_refresh():
    # check that quotes are constantly running
    query_sec = "SELECT max(last_upd) FROM public.secquotesdiff;"
    query_fut = "select max(last_upd) from public.futquotesdiff;"
    try:
        last_sec = sql.get_table.query_to_list(query_sec)[0]['max'].replace(tzinfo=None)
        last_fut = sql.get_table.query_to_list(query_fut)[0]['max'].replace(tzinfo=None)
        logger.debug(f"last_sec {last_sec}, last_fut {last_fut}, time_bound: {datetime.now() - timedelta(minutes=10)}")
        if min(last_fut, last_sec) < datetime.now() - timedelta(minutes=10):
            asyncio.run(telegram.send_message(f"quotes import problems: sec: {last_sec} fut: {last_fut}", urgent=True))
    except:
        asyncio.run(telegram.send_message(f"quotes import problems: 0 records", urgent=True))


@sync_timed()
def check_quotes_import_emptytable():
    # check that tables are not empty
    tables = ['pos_fut', 'pos_money', 'pos_eq']  # , 'pos_collat']
    for table in tables:
        query = f"select count(*) as cnt from public.{table}"
        cnt = sql.get_table.query_to_list(query)[0]['cnt']
        if int(cnt) == 0:
            asyncio.run(telegram.send_message(f"table {table} is empty", urgent=True))


@sync_timed()
def check_quotes_import_money():
    # check that money are imported
    query = "SELECT count(*) as cnt_rows, count(money) as cnt_money FROM public.money;"
    cnt_rows = sql.get_table.query_to_list(query)[0]['cnt_rows']
    cnt_money = sql.get_table.query_to_list(query)[0]['cnt_money']
    if (cnt_rows, cnt_money) != (2, 2):
        asyncio.run(telegram.send_message(f"public.money error: {(cnt_rows, cnt_money)}", urgent=True))

    query_sec = "select count(*), code from secquotes group by code having count(*) >= 2;"
    query_fut = "select count(*), code from futquotes group by code having count(*) >= 2;"

    sec_qty, fut_qty = len(sql.get_table.query_to_list(query_sec)), len(sql.get_table.query_to_list(query_fut))
    if (sec_qty, fut_qty) != (0, 0):
        asyncio.run(telegram.send_message(f"(sec, fut) doubling: {(sec_qty, fut_qty)}", urgent=True))


@sync_timed()
def check_quotes_import_5min():
    # check candles import is running
    query_candles = "SELECT count(*) as cnt from  df_all_candles_t where datetime > now() - interval '5 minutes'"
    cnt_rows = sql.get_table.query_to_list(query_candles)[0]['cnt']
    if cnt_rows == 0:
        asyncio.run(telegram.send_message(f"tinkoff candles import error: no candles for the last 5 mins", urgent=True))


@sync_timed()
def pos_orders_gen():
    query = """
    begin;
    insert into public.orders_my (state, quantity, remains, comment, stop_loss, take_profit, barrier, max_amount, pause, code, direction, start_time)
    SELECT state, quantity, 0, comment, stop_loss, take_profit, barrier, max_amount, pause, code, direction, start_time	FROM public.trd_pos
    where comment not in (select comment from public.orders_my where end_time is null);
    commit;
    """
    sql.get_table.exec_query(query)


def format_volumes(df):
    df['end_time'] = df['end_time'].apply(lambda x: x.strftime("%H:%M"))
    df['std'] = df['std'].apply(lambda x: round(x, 1))
    for col in ['volume_mean',   'volume_std',    'volume']:
        df[col] = df[col].apply(lambda x: int(x))

    return df[['security', 'std' ,'end_time','timeframe','volume_mean', 'volume_std'  ]]


def format_jumps(df):
    df['cdate_x'] = df['cdate_x'].apply(lambda x: x.strftime("%H:%M"))
    df['inc'] = df['inc'].apply(lambda x: round(x, 2))
    df['close_x'] = df['close_x'].apply(lambda x: round(x, 4))
    return df[['security', 'inc','close_x', 'cdate_x']]


if __name__ == '__main__':
    logger.info("monitor started: ")
    check_quotes_import()

    if not tools.clean_processes.clean_proc("monitor", os.getpid(), 4):
        logger.info("something is already running")
        exit(0)

    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    logger.info("urgent_list:" + str(urgent_list))

    df_monitor = update_tables(filtered=False)
    logger.debug('df_monitor' + df_monitor.head().to_string())
    logger.debug(df_monitor.code.drop_duplicates())

    # pos_orders_gen()
    # print("pos_orders_gen")

    df_gains, df_inc = get_gains()
    logger.debug(f'df_gains: \n{df_gains.head()}')
    send_df(format_jumps(df_gains[df_gains['security'].isin(urgent_list)]), True)
    send_df(format_jumps(df_gains[~df_gains['security'].isin(urgent_list)]), False)

    df_volumes = get_abnormal_volumes()
    send_df(format_volumes(df_volumes[df_volumes['security'].isin(urgent_list)]), True)
    send_df(format_volumes(df_volumes[~df_volumes['security'].isin(urgent_list)]), False)

    df_bollinger = get_bollinger()

    if len(pd.concat([df_volumes['security'], df_gains['security']])) > 0:
        prepare_images(pd.concat([df_volumes['security'], df_gains['security']]).drop_duplicates())
        send_gains(df_gains, urgent_list)
        send_abnormal_volumes(df_volumes, urgent_list)

    df_inc['close_x'] = df_inc['close_x'].astype(str).replace(r'0+$', '', regex=True)
    send_df(df_inc)

    if len(df_bollinger) > 0:
        logger.info("sending bollinger")
        df_bollinger['quote'] = df_bollinger['quote'].round(8)
        df_bollinger['quote'] = df_bollinger['quote'].astype(str).replace(r'0+$', '', regex=True)
        logger.info(df_bollinger)
        send_df(df_bollinger)
    logger.info("monitor: ended")
