import logging
import os
import sys

from matplotlib import pyplot as plt
from sqlalchemy.util import asyncio

import sql.get_table
import telegram
from tools.utils import sync_timed
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('my.env'), verbose=True)
print('finddotenv', find_dotenv('my.env'))

IMAGES_PATH = os.path.join(os.environ['root_path'], f'monitor/level_images')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(handler)


def send_all_graph(interesting_sec, urgent_list):
    print(interesting_sec, urgent_list)
    if len(interesting_sec) > 0:
        prepare_images(interesting_sec.drop_duplicates())
        send_sec_graph(interesting_sec.drop_duplicates(), urgent_list)
    logger.debug(f"{len(interesting_sec)} images to be sent")


@sync_timed()
def send_sec_graph(df_gains, urgent_list=None):
    logger.info("DEBUG send_sec_graph")
    logger.info(df_gains)
    logger.info(urgent_list)
    if urgent_list is None:
        urgent_list = []
    for idx, row in df_gains.items():
        is_urgent = (row in urgent_list)
        path = os.path.join(IMAGES_PATH, f'{row}.png')
        asyncio.run(telegram.send_photo(path, is_urgent))


@sync_timed()
def send_df(df, is_urgent=False):
    if len(df) > 0:
        asyncio.run(telegram.send_message(df.to_csv(index=False, sep='\t').expandtabs(8), is_urgent))

@sync_timed()
def prepare_images(df_monitor_code_series, days_to_subtract=7):
    logger.info(f"preparing images for: {df_monitor_code_series}")
    query = f"""
    select  security, close, datetime from df_all_candles_t  where datetime >= date(NOW() -  interval '{days_to_subtract + 1} days')
	order by security, datetime asc
    """

    df = sql.get_table.query_to_df(query)

    query = f"select * from public.df_levels"
    df_eq = sql.get_table.query_to_df(query)

    query = f"select * from public.df_all_volumes"
    df_volumes = sql.get_table.query_to_df(query)

    for sec in df_monitor_code_series:
        df_ = df[df['security'] == sec]
        df_eq_ = df_eq[df_eq['sec'] == sec]
        df_volumes_ = df_volumes[df_volumes['code'] == sec]
        plot_price_volume(df_, df_eq_, df_volumes_,
                          title=f"{sec} {datetime.now()}", filename=f"{sec}")
        plt.close('all')


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
    for _, row in df_eq.iterrows():
        ax_left.axhline(y=row['price'], color='r', linestyle='-')
    plt.savefig(os.path.join(IMAGES_PATH, f'{filename}.png'), dpi=50)
