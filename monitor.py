import datetime

import pandas as pd
import telegram
import asyncio
import matplotlib.pyplot as plt
import sql.get_table
import config.sql_queries
from datetime import datetime, timedelta
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('monitor')
engine = sql.get_table.engine

def copy_colvals(df_monitor, colpairs, is_upd_only=False):
    for pairs in colpairs:
        if is_upd_only == False:
            df_monitor.loc[df_monitor[pairs[1]].notnull(), pairs[0]] = df_monitor.loc[
                df_monitor[pairs[1]].notnull(), pairs[1]]
        else:
            df_monitor.loc[df_monitor['to_update'] & df_monitor[pairs[1]].notnull(), pairs[0]] = df_monitor.loc[
                df_monitor['to_update'] & df_monitor[pairs[1]].notnull(), pairs[1]]

    return df_monitor


def update_tables(filtered=False):
    df_monitor = []

    try:
        df_monitor = pd.DataFrame(engine.execute(
            "select code, old_state, old_price, old_start, old_end, new_state, new_price, new_start, new_end, std, "
            "old_timestamp, new_timestamp from public.df_monitor"))
    except:
        pass

    if len(df_monitor) == 0:
        df_monitor = pd.DataFrame([], columns=['code', 'old_state', 'old_price', 'old_start', 'old_end', 'new_state',
                                               'new_price', 'new_start', 'new_end', 'std', 'old_timestamp',
                                               'new_timestamp'])
        df_monitor.to_sql('df_monitor', engine, if_exists='append')

    columns = df_monitor.columns

    if filtered:
        query = config.sql_queries.monitor["filtered_query"]
    else:
        query = config.sql_queries.monitor["non_filtered_query"]

    df_new = pd.DataFrame(engine.execute(query))
    df_monitor = df_monitor.merge(df_new, how='outer', on='code')

    print(df_new.head(), df_monitor.head())
    # переносим not null новое в старое и переносим цену и стд
    colpairs = [('old_price', 'new_price'), ('old_state', 'new_state'), ('old_start', 'new_start'), \
                ('old_end', 'new_end'), ('old_timestamp', 'new_timestamp'), ('new_price', 'price'), ('std', 'new_std'),
                ('new_timestamp', 'timestamp')]

    df_monitor = copy_colvals(df_monitor, colpairs)
    print("step2", df_monitor.head())

    # тестим
    df_monitor['to_update'] = df_monitor['new_state'].isnull() | (
            df_monitor['new_price'] + df_monitor['std'] < df_monitor['old_start']) | \
                              (df_monitor['new_price'] - df_monitor['std'] > df_monitor['old_end'])

    colpairs = [('new_state', 'state'), ('new_start', 'start'), ('new_end', 'end')]

    df_monitor = copy_colvals(df_monitor, colpairs, is_upd_only=True)
    print("step3", df_monitor.head(), df_monitor['to_update'], df_monitor[df_monitor['to_update']])

    sql.get_table.exec_query("delete from public.df_monitor")
    df_monitor[columns].to_sql('df_monitor', engine, if_exists='append')

    return df_monitor[df_monitor['to_update']]


def send_messages(df_monitor):
    for idx, row in df_monitor.iterrows():
        before = (round(row['old_price'], 4), row['old_state'], round(row['old_start'], 4), round(row['old_end'], 4))
        after = (round(row['new_price'], 4), row['new_state'], round(row['new_start'], 4), round(row['new_end'], 4))

        state_msg = f" {round(((row['new_price'] - row['old_price']) * 100 / row['old_price']), 2)} "

        msg = f'{row["code"]} {state_msg}: {before} ->\n {after}'

        logger.info(msg)
        asyncio.run(telegram.send_message(msg))
        asyncio.run(telegram.send_photo(f'./level_images/{row["code"]}.png'))


def create_big_deals_image(code):
    query = f"select * from public.bigdealshist where price_inc <> 0 and code='{code}'"
    df_monitor = pd.DataFrame(engine.execute(query))

    if len(df_monitor) > 0:
        pd.plotting.register_matplotlib_converters()
        plt.figure(figsize=(16, 9), dpi=80)

        colors = ['g' if x > 0 else 'r' for x in df_monitor['price_inc']]

        plt.xticks(rotation=90)
        plt.locator_params(axis='y', nbins=20)
        plt.locator_params(axis='x', nbins=20)
        plt.title(code)

        times = [datetime.strptime(x[0:5], '%H:%M').time() for x in df_monitor['snaptimestamp'].astype(str)]
        plt.scatter(x=times, y=df_monitor['lastprice'], s=df_monitor['volume_inc'] * 20, c=colors)
        plt.savefig(f'./level_images/{code}_big_deals.png')
    return len(df_monitor)


def prepare_images(df_monitor_code_series):
    days_to_subtract = 7
    CANDLES_PATH = './Data/candles.csv'

    df = pd.read_csv(CANDLES_PATH, sep='\t')
    df['t'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M')
    start_date = datetime.today() - timedelta(days=days_to_subtract)
    df = df[df['t'] > start_date]

    query = f"select * from public.bigdealshist where price_inc <> 0"  # and code='SBER'"
    df_bigdealshist = pd.DataFrame(engine.execute(query))
    df_bigdealshist['datetime'] = df_bigdealshist['tradedate'].astype(str) + " " + df_bigdealshist[
                                                                                       'snaptimestamp'].astype(str).str[
                                                                                   :5]

    df_bigdealshist = df.reset_index().merge(df_bigdealshist, how='inner', right_on=['code', 'datetime'],
                                             left_on=['security', 'datetime'])

    query = f"select * from public.df_levels"  # and code='SBER'"
    df_eq = pd.DataFrame(engine.execute(query))

    query = f"select * from public.df_all_volumes"  # and code='SBER'"
    df_volumes = pd.DataFrame(engine.execute(query))

    for sec in df_monitor_code_series:
        logger.info(sec)
        df_ = df[df['security'] == sec]
        df_eq_ = df_eq[df_eq['sec'] == sec]
        df_volumes_ = df_volumes[df_volumes['code'] == sec]
        df_bigdealshist_ = df_bigdealshist[df_bigdealshist['security'] == sec]
        plot_price_volume(df_, df_eq_, df_volumes_, df_bigdealshist_[['index', 'close', 'volume_inc', 'price_inc']],
                          title=f"{sec} {datetime.now()}", filename=f"{sec}")
    logger.info("Monitor: graphs updated")


def plot_price_volume(df, df_eq, df_volumes, df_bigdealshist, title="title", filename="fig"):
    fig, ax_left = plt.subplots()
    plt.xticks(rotation=90)
    fig.set_figheight(9)
    fig.set_figwidth(16)
    fig.align_ylabels()

    ax_right = ax_left.twiny()
    if len(df_volumes) > 0:
        ax_right.plot(df_volumes['volume'], df_volumes['price'], color='green', linestyle='dashed')
        ax_right.axis(xmax=max(df_volumes['volume']) * 3)

    #ax_left.locator_params(axis='x', nbins=50)
    ax_left.locator_params(axis='y', nbins=20)
    ax_left.set_xticklabels(df['datetime'])
    ax_left.plot(df['t'],df['close'])

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

    colors = ['g' if x > 0 else 'r' for x in df_bigdealshist['price_inc']]
    if len(df_bigdealshist) > 0:
        ax_left.scatter(x=df_bigdealshist['index'], y=df_bigdealshist['close'], s=df_bigdealshist['volume_inc'] * 20,
                        c=colors)
    logger.info("Monitor: Saving file")
    plt.savefig(f'./level_images/{filename}.png', dpi=50)


def get_gains(path='./Data/candles.csv', min_lag=10, threshold=0.5):
    df = pd.read_csv(path, sep='\t')
    df['cdate'] = pd.to_datetime(df['datetime'], format="%d.%m.%Y %H:%M")

    start_date = datetime.now() - timedelta(minutes=min_lag)
    # end_date = datetime.datetime.now() - datetime.timedelta(minutes=0)

    df_start = df[df['cdate'] < start_date]
    df_end = df  # [df['cdate'] < end_date]

    df_start = df_start.sort_values(['security', 'cdate']).groupby(['security']).tail(1)
    df_end = df_end.sort_values(['security', 'cdate']).groupby(['security']).tail(1)

    df_res = df_end.merge(df_start, how='inner', on='security')[
        ['security', 'class_code_x', 'close_x', 'close_y', 'cdate_x', 'cdate_y']]
    df_res['inc'] = (df_res['close_x'] / df_res['close_y'] - 1) * 100

    df_fut = df_res[df_res['class_code_x'] == 'SPBFUT'].sort_values('inc').reset_index()
    df_eq = df_res[df_res['class_code_x'] != 'SPBFUT'].sort_values('inc').reset_index()
    df_inc = pd.concat([df_eq.head(5), df_eq.tail(5), df_fut.head(5), df_fut.tail(5)])[['security', 'inc', 'close_y']]\
        .sort_values('inc').reset_index()

    return df_res[(df_res['inc'] >= threshold) | (df_res['inc'] <= -threshold)], df_inc


def send_gains(df_gains, urgent_list=None):
    logger.info("df_info:", df_inc.to_string(justify='left', index=False))
    if urgent_list is None:
        urgent_list = []
    for idx, row in df_gains.iterrows():
        before = round(row['close_y'], 4)
        after = round(row['close_x'], 4)
        inc = round(row['inc'], 2)

        msg = f'{row["security"]} {inc}: {before} -> {after}  {row["cdate_x"]}'
        is_urgent = (row["security"] in urgent_list)
        logger.info(msg)
        asyncio.run(telegram.send_message(msg, is_urgent))
        asyncio.run(telegram.send_photo(f'./level_images/{row["security"]}.png', is_urgent))


def get_abnormal_volumes(include_daily=True, minutes_lookback=10, days_lookback=14, path='./Data/candles.csv'):
    def get_volumes(minutes_lookback=minutes_lookback, days_lookback=days_lookback, path=path):
        start_time = (datetime.now() - timedelta(minutes=minutes_lookback)).time()
        end_time = (datetime.now()).time()

        start_date = (datetime.now() - timedelta(days=days_lookback)).date()
        end_date = (datetime.now()).date()

        df = pd.read_csv(path, sep='\t')
        df['cdate'] = pd.to_datetime(df['datetime'], format="%d.%m.%Y %H:%M")
        df['ctime'] = df['cdate'].dt.time
        df['cdt'] = df['cdate'].dt.date

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
        return df_analys[df_analys['std'] >= 4].sort_values('std', ascending=False)

    df_minutes = get_volumes()
    df_minutes['timeframe'] = 'mins'

    df_daily = get_volumes(minutes_lookback=540) if include_daily else pd.DataFrame()
    df_daily['timeframe'] = 'days'

    return pd.concat([df_minutes, df_daily], axis=0).reset_index()


def send_abnormal_volumes(df_volumes, urgent_list=None):
    if urgent_list is None:
        urgent_list = []
    for idx, row in df_volumes.iterrows():
        msg = f'{row["security"]} {row["timeframe"]} {round(row["std"], 1)}: \
vol:{int(row["volume"])} avg:{int(row["volume_mean"])} std:{int(row["volume_std"])} {row["end_time"]}'
        logger.info(msg)
        is_urgent = (row["security"] in urgent_list)
        asyncio.run(telegram.send_message(msg, is_urgent))
        if row["timeframe"] == 'daily':
            asyncio.run(telegram.send_photo(f'./level_images/{row["security"]}.png', is_urgent))


def get_bollinger():
    query = """SELECT code, quote, round(bollinger::numeric,2) as bollinger, count, 
round(up::numeric,2) as up, round(down::numeric,2) as down
FROM public.quote_bollinger 
where (class_code = 'SPBFUT' and abs(bollinger) > 1.7) 
or abs(bollinger) > 2 
or code in (select code from public.pos_bollinger);"""
    return pd.DataFrame(sql.get_table.exec_query(query))


def send_df(df_bollinger):
    asyncio.run(telegram.send_message(df_bollinger.to_string(justify='left',index=False)))


if __name__ == '__main__':
    logger.info(datetime.now())
    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    logger.info("urgent_list:",urgent_list)
    df_monitor = update_tables(filtered=False)
    print('df_monitor', df_monitor.head())
    logger.info(df_monitor.code.drop_duplicates())
    df_gains, df_inc = get_gains()
    logger.info('df_gains', df_gains.head())
    df_volumes = get_abnormal_volumes()

    df_bollinger = get_bollinger()

    if len(pd.concat([df_volumes['security'], df_gains['security']])) > 0:
        # if len(df_gains['security']) > 0:
        prepare_images(pd.concat([df_volumes['security'], df_gains['security']]).drop_duplicates())
        # prepare_images(df_gains['security'].drop_duplicates())
        # send_messages(df_monitor)
        send_gains(df_gains, urgent_list)
        send_abnormal_volumes(df_volumes, urgent_list)

    send_df(df_inc)
    if len(df_bollinger) > 0:
        logger.info("sending bollinger")
        send_df(df_bollinger)
    logger.info("monitor: ended", datetime.now())
