#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.geeksforgeeks.org/how-to-schedule-python-scripts-as-cron-jobs-with-crontab/
import asyncio
import os

import pandas as pd
import numpy as np
import config.sql_queries
from datetime import datetime, timedelta
from scipy.signal import find_peaks
# from sqlalchemy import create_engine
import time
import sql.get_table
import telegram
import pytz

import tools.clean_processes

CANDLES_PATH = './Data/candles.csv'
engine = sql.get_table.engine


def load_df(days_to_subtract=7):
    df = sql.get_table.query_to_df("select * from df_all_candles_t") #pd.read_csv(CANDLES_PATH, sep='\t')

    #df['t'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M')
    df['t'] = pd.to_datetime(df['datetime'])
    df.drop(columns=['datetime'], inplace=True)

    df['week'] = df['t'].dt.isocalendar().week
    df['day'] = df['t'].dt.day
    current_week = datetime.today().isocalendar().week
    current_day = datetime.today()

    df = df[(df['volume'] > 0) & (df['close'] > 0)]

    # Adjust start date
    start_date = (datetime.today() - timedelta(days=days_to_subtract))
    start_date = start_date.replace(tzinfo=df['t'][0].tzinfo)

    df = df[df['t'] > start_date] #np.datetime64(start_date)]

    # adjust past week volume
    df.loc[df['week'] != current_week, 'volume'] = df.loc[df['week'] != current_week, 'volume'] / 2
    df.loc[df['day'] == current_day, 'volume'] = df.loc[df['day'] == current_day, 'volume'] * 2
    return df


def build_levels(df_):
    df_levels = pd.DataFrame()
    df_all_levels = pd.DataFrame()
    df_all_volumes = pd.DataFrame()

    for eq in df_['security'].drop_duplicates():

        df = df_[df_['security'] == eq]
        df = df.reset_index()
        std = np.std((df['close'] - df['close'].shift(1)))
        print(eq, std)
        np_close = np.array(df['close'])

        price_range = []
        volumes = []
        mult = 100

        for x in np.linspace(np.min(np_close), np.max(np_close), mult):
            price_range.append(x)
            volumes.append(np.dot(df['volume'], ((np_close > x - std) & (np_close < x + std))))
        volumes = np.convolve(volumes, np.ones(10), mode='same')

        idx, _ = find_peaks(volumes)
        peaks = list(zip([price_range[t] for t in idx], [volumes[t] for t in idx]))

        peaks.insert(0, (np.min(np_close), 0))
        peaks.insert(len(peaks), (np.max(np_close), 0))

        for _ in range(1, len(peaks)):
            for i in range(1, len(peaks)):
                if peaks[i][0] - peaks[i - 1][0] < 2 * std:
                    # print(peaks)
                    if peaks[i][1] < peaks[i - 1][1]:
                        # print("del", i)
                        del peaks[i]
                    else:
                        # print("del", i - 1)
                        del peaks[i - 1]
                    # print("after:", peaks)
                    break

        # print(peaks)

        df_eq = pd.DataFrame(peaks, columns=['price', 'volume'])
        df_eq['std'] = std
        df_eq['sec'] = eq
        df_eq[['min_start', 'max_start', 'end', 'sl', 'mid', 'down', 'prev_end', 'next_sl']] = None  ##

        max_level = 0.3
        close_level = 0.9
        sl_level = 0.8

        # build levels
        for idx, row in df_eq.iterrows():
            if idx >= 1:  # >= если хотим ловить падающий нож
                df_eq.loc[idx, 'mid'] = df_eq.loc[idx - 1, 'price'] if idx >= 1 else 0
                df_eq.loc[idx, 'down'] = df_eq.loc[idx - 2, 'price'] if idx >= 2 else 0

                min_start = df_eq.loc[idx, 'mid'] + row['std']
                max_start = df_eq.loc[idx, 'mid'] + (row['price'] - df_eq.loc[idx, 'mid']) * max_level
                sl = min((sl_level - 1) * (df_eq.loc[idx, 'mid'] - df_eq.loc[idx, 'down']) + df_eq.loc[idx, 'mid'],
                         df_eq.loc[idx, 'mid'] - 2 * row['std'])

                if min_start < max_start:
                    df_eq.loc[idx, 'min_start'] = min_start
                    df_eq.loc[idx, 'max_start'] = max_start
                    df_eq.loc[idx, 'end'] = df_eq.loc[idx, 'mid'] + (row['price'] - df_eq.loc[idx, 'mid']) * close_level
                    df_eq.loc[idx, 'sl'] = sl

        # fill prev-next sl
        for idx, row in df_eq.iterrows():
            df_eq.loc[idx, 'prev_end'] = (df_eq.loc[idx - 1, 'end'] if idx - 1 >= 0 else None)
            df_eq.loc[idx, 'next_sl'] = (df_eq.loc[idx + 1, 'sl'] if idx + 1 < len(df_eq) else None)

        # creating price-volume df
        df_price_volume = pd.DataFrame({"price": price_range, "volume": volumes})
        df_price_volume['code'] = eq
        # print(df_price_volume)

        # create 1 level 1 row table
        df_eq_all_levels = create_all_levels(df_eq)
        df_eq_all_levels['std'] = std
        df_eq_all_levels = compress_all_levels(df_eq_all_levels)

        df_levels = pd.concat([df_levels, df_eq])
        df_all_levels = pd.concat([df_all_levels, df_eq_all_levels])
        df_all_volumes = pd.concat([df_all_volumes, df_price_volume])

        df_levels['implied_prob'] = ((df_levels['min_start'] + df_levels['max_start']) / 2 - df_levels['sl']) / (
                df_levels['end'] - df_levels['sl'])
    return df_levels, df_all_levels, df_all_volumes


def create_all_levels(df_levels):
    df_all_levels = pd.DataFrame([], columns=['code', 'name', 'start', 'end', 'logic'])
    for idx, row in df_levels.iterrows():
        if idx == 0:
            # print(row['next_sl'])
            if row['next_sl']:
                df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'new_low', 0, row['next_sl'], 0)
            else:
                df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'new_low', 0, row['price'], 0)

        if (not row['prev_end']) and (not row['sl']) and (not row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['mid'], row['price'], 1)

        elif (not row['prev_end']) and (not row['sl']) and (row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['mid'], row['next_sl'], 2)

        elif (not row['prev_end']) and (row['sl']) and (not row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_start', row['sl'], row['min_start'], 3)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'start', row['min_start'], row['max_start'], 3)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['max_start'], row['end'], 3)

        elif (not row['prev_end']) and (row['sl']) and (row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_start', row['sl'], row['min_start'], 4)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'start', row['min_start'], row['max_start'], 4)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['max_start'], row['next_sl'], 4)
            # df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_tp', row['next_sl'],row['end'],4)

        elif (row['prev_end']) and (not row['sl']) and (not row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['prev_end'], row['price'], 5)

        elif (row['prev_end']) and (not row['sl']) and (row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['prev_end'], row['next_sl'], 6)

        elif (row['prev_end']) and (row['sl']) and (not row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_tp', row['sl'], row['prev_end'], 7)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'tp_start', row['prev_end'], row['min_start'], 7)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'start', row['min_start'], row['max_start'], 7)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['max_start'], row['end'], 7)

        elif (row['prev_end']) and (row['sl']) and (row['next_sl']):
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_tp', row['sl'], row['prev_end'], 8)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'tp_start', row['prev_end'], row['min_start'], 8)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'start', row['min_start'], row['max_start'], 8)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'observe', row['max_start'], row['next_sl'], 8)
            # df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'sl_tp', row['next_sl'], row['end'],8)

        else:
            pass

        if idx == len(df_levels) - 1:
            if row['sl']:
                df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'tp_new_high', row['end'], row['price'], 9)
            df_all_levels.loc[len(df_all_levels)] = (row['sec'], 'new_high', row['price'], 999999, 9)

    return df_all_levels


def compress_all_levels(df_all_levels):
    for idx in reversed(df_all_levels.index):
        if idx >= 1:
            if not df_all_levels.loc[idx, 'start']:
                df_all_levels.drop(idx, inplace=True)
            elif df_all_levels.loc[idx, 'name'] == df_all_levels.loc[idx - 1, 'name'] \
                    and df_all_levels.loc[idx, 'start'] == df_all_levels.loc[idx - 1, 'end']:
                df_all_levels.loc[idx - 1, 'end'] = df_all_levels.loc[idx, 'end']
                df_all_levels.drop(idx, inplace=True)
            elif df_all_levels.loc[idx, 'start'] != df_all_levels.loc[idx - 1, 'end']:
                print(f'INCONSISTENCY!!! {df_all_levels.iloc[[idx]]} {df_all_levels.iloc[[idx - 1]]}')
    df_all_levels['start'] = pd.to_numeric(df_all_levels['start'])
    df_all_levels['end'] = pd.to_numeric(df_all_levels['end'])
    return df_all_levels


def update_db_tables(df_levels, df_all_levels, df_all_volumes):

    df_levels['timestamp'] = datetime.now()
    df_all_levels['timestamp'] = datetime.now()

    try:
        engine.execute(config.sql_queries.config["drop_view"])
    except:
        pass

    sql.get_table.exec_query("delete from public.df_levels")
    sql.get_table.exec_query("delete from public.df_all_levels")
    sql.get_table.exec_query("delete from public.df_all_volumes")

    df_levels.to_sql('df_levels', engine, if_exists='append')
    df_all_levels.to_sql('df_all_levels', engine, if_exists='append')
    # engine.execute(config.sql_queries.config["create_view"])
    df_all_volumes.to_sql('df_all_volumes', engine, if_exists='append')


if __name__ == '__main__':
    startTime = time.time()

    print(time.ctime())
    if not tools.clean_processes.clean_proc("update_levels", os.getpid(), 5):
        print("something is already running")
        exit(0)

    df = load_df()
    df_levels, df_all_levels, df_all_volumes = build_levels(df)
    update_db_tables(df_levels, df_all_levels, df_all_volumes)

    asyncio.run(telegram.send_message(f'перестройка уровней выполнена за {(time.time() - startTime):.2f} с'))
    print(f'перестройка уровней выполнена за {(time.time() - startTime):.2f} с')
