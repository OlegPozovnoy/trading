from pymongo import MongoClient
from datetime import datetime, timedelta
import sql.get_table
import pandas as pd
import matplotlib.pyplot as plt


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
    dt = dt + shift
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

    print(df)
    if len(df) == 0:
        return pd.DataFrame()

    time_bound = df.loc[df['datetime']<=(news_dt+shift).replace(second=0, microsecond=0)]['datetime'].max()
    mean_idx = df.loc[df['datetime'] == time_bound].index[0]
    print(mean_idx, news_dt)

    df['spread'] = df['high'] - df['low']
    df['move'] = df['open'] - df.iloc[mean_idx]['open']
    df['volume_inc'] = df['volume'] - df['volume'].shift()
    df['open_inc'] = df['open'] - df['open'].shift()


    df['avg_before'] = df[max(0,mean_idx-15):mean_idx+1]['open'].mean()
    df['avg_after'] = df[mean_idx+1:]['close'].mean()
    print(df.dtypes)
    return df, mean_idx



def create_analytics(channel, code, news_dt):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.expand_frame_repr', False)

    df, mean_idx = get_news_df(code, news_dt)
    print(df)

    fig, ax_left = plt.subplots()
    fig.set_figheight(9)
    fig.set_figwidth(16)
    ax_right = ax_left.twinx()

    ax_left.plot(df.index, df['open'])
    ax_left.plot(df.index, df['high'])
    ax_left.plot(df.index, df['low'])
    ax_right.bar(df.index, df['volume'])

    ax_right.axis(ymax=max(df['volume']) * 3)
    ax_left.axhline(y=df.iloc[0]['avg_before'], color='r', linestyle='-')
    ax_left.axhline(y=df.iloc[0]['avg_after'], color='b', linestyle='-')
    plt.axvline(x=mean_idx)

    fig_title = f"{channel} {code} {news_dt}"
    plt.title(fig_title)
    plt.savefig(f"./news_images/{fig_title}")
    return df


channel = ""
code = 'OZM3'
news_dt = datetime.strptime("2023-03-27 15:48:39", '%Y-%m-%d %H:%M:%S')


create_analytics(channel, code, news_dt)