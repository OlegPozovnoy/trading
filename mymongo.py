import json

from pymongo import MongoClient
from datetime import timedelta
import sql.get_table
import pandas as pd
import matplotlib.pyplot as plt
import pytz

from nlp.mongo_tools import get_news_from_channels

client = MongoClient()
engine = sql.get_table.engine


def import_synonims():
    names_collection = client.trading['trading']

    for document in names_collection.find():
        print([document['ticker']] + [x.strip() for x in document['name'].split(',')])  # iterate the cursor
        new_list = [document['ticker']] + [x.strip() for x in document['name'].split(',')]
        # document['name'] = [document['ticker']] + [x.strip() for x in document['name'].split(',')]
        names_collection.update_one(document, {'$set': {'namee': new_list}})


def query_for_hist(code, dt, shift):
    #dt = dt + shift
    dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"corrected date {dt}")
    query = f"""
    SELECT open, high, low, close, volume, security, datetime
	FROM public.df_all_candles_t where security = '{code}' 
	and datetime between '{dt_str}'::timestamp - interval '60 minutes' and '{dt_str}'::timestamp + interval '60 minutes'
	order by datetime asc
    """
    print(query)
    return query


def get_news_df(code, news_dt, mins_spread = 60, shift=timedelta(hours=-3)):
    query = query_for_hist(code=code, dt=news_dt, shift=shift)
    df = pd.DataFrame(engine.execute(query))

    print(df, df.dtypes)
    if len(df) == 0:
        return pd.DataFrame(), None, None

    lower_bound = news_dt.replace(second=0, microsecond=0)
    print(lower_bound)
    time_bound = df.loc[df['datetime']<=lower_bound]['datetime'].max()
    if pd.isnull(time_bound):
        return pd.DataFrame(), None, None

    print(time_bound)
    mean_idx = df.loc[df['datetime'] == time_bound].index[0]
    print(mean_idx, news_dt)

    df['spread'] = df['high'] - df['low']
    df['move'] = df['open'] - df.iloc[mean_idx]['open']
    df['volume_inc'] = df['volume'] - df['volume'].shift()
    df['open_inc'] = df['open'] - df['open'].shift()

    analytics=dict()

    df_before=df[max(0,mean_idx-15):mean_idx]
    if len(df_before) == 0:
        return pd.DataFrame(), None, None

    df_current=df[mean_idx:mean_idx+2]
    df_after=df[mean_idx+2:]

    analytics['avg_before'] = df_before['close'].mean()
    analytics['volume_before'] = int(df_before['volume'].max())
    analytics['spread_before'] = df_before['high'].max()- df_before['low'].min()

    analytics['volume_current'] = int(df_current['volume'].max())
    analytics['spread_current'] = df_current['high'].max()- df_current['low'].min()

    analytics['avg_after'] = df_after['close'].mean()
    analytics['avg_prct'] = analytics['avg_after']/analytics['avg_before'] - 1
    print(df.dtypes)
    return df, mean_idx, analytics



def create_analytics(channel, code, news_dt, figtext=''):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.expand_frame_repr', False)

    df, mean_idx, analytics = get_news_df(code, news_dt)
    print(df)
    if mean_idx is None: return df, {} # например новость на выхах

    plt.gca()
    fig, ax_left = plt.subplots()
    #fig.set_figheight(9)
    #fig.set_figwidth(16)
    ax_right = ax_left.twinx()

    ax_left.plot(df.index, df['open'])
    ax_left.plot(df.index, df['high'])
    ax_left.plot(df.index, df['low'])
    ax_right.bar(df.index, df['volume'])

    ax_right.axis(ymax=max(df['volume']) * 3)
    ax_left.axhline(y=analytics['avg_before'], color='r', linestyle='-')
    ax_left.axhline(y=analytics['avg_after'], color='b', linestyle='-')
    plt.axvline(x=mean_idx)

    fig_title = f"{channel} {news_dt} {code} "
    plt.title(fig_title)
    plt.text(x=-1, y=1, s=str(json.dumps(analytics, indent=1, sort_keys=True)), va="bottom", ha="left")
    #plt.tight_layout()
    plt.savefig(f"./news_images/{fig_title}.png")
    return df, analytics


def analysis_channel(username):
    news = get_news_from_channels(username)
    for item in news:
        for code in item['tags']:
            channel = username
            news_dt = pytz.timezone('Europe/Moscow').localize(item['date'])
            text = str(item['caption']) + ' ' + str(item['text'])
            _, analytics =  create_analytics(channel, code, news_dt, text)

