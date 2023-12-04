import os
import json
import subprocess

from dotenv import load_dotenv
import logging
import sql
import datetime
from sql import get_table
from prophet import Prophet
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
from nlp import client

load_dotenv(dotenv_path='./my.env')
settings_path = os.environ['instrument_list_path']
check_list = ['RIZ3', 'CRZ3', 'MXZ3', 'SiZ3']
cutoffs = [datetime.time(10, 0, 0),
           datetime.time(12, 0, 0),
           datetime.time(14, 0, 0),
           datetime.time(18, 45, 0),
           datetime.time(23, 45, 0)]
logger = logging.getLogger()
logger.setLevel(logging.INFO)

with open(settings_path, "r") as fp:
    settings = json.load(fp)
tickers = settings["futures"]["secCodes"] + settings["equities"]["secCodes"]
logger.info(tickers)

df_ = sql.get_table.load_candles_cutoff(cutofftimes=cutoffs)
df_ = df_[df_['security'].isin(tickers)]
df_['t'] = pd.to_datetime(df_['datetime'], format='%d.%m.%Y %H:%M')
df_['dt'] = df_['t'].dt.date
df_['time'] = df_['t'].dt.time


def get_time_cutoff_df(end_cutoff):
    df_bollinger = df_[df_['time'] <= end_cutoff] \
        .sort_values(['security', 'class_code', 'dt', 'time'], ascending=False) \
        .groupby(['security', 'class_code', 'dt']) \
        .head(1) \
        .reset_index()
    print(df_bollinger)
    df_bollinger['dtime'] = df_bollinger.apply(lambda x: datetime.datetime.combine(x['dt'], end_cutoff), axis=1)
    return df_bollinger


dfs = [get_time_cutoff_df(dt) for dt in cutoffs]
df_pivot = pd.concat(dfs).sort_values(['security', 'class_code', 'dtime'], ascending=False)
df_pivot['wd'] = df_pivot['dt'].apply(lambda x: x.weekday())
df_pivot = df_pivot[df_pivot['wd'] < 5]
logger.info(df_pivot)

df_pivot = df_pivot[['close', 'security', 'dtime']]


def predict(sec):
    df = df_pivot[df_pivot['security'] == sec]
    df_p = pd.DataFrame()
    df_p['ds'] = df['dtime']
    df_p['y'] = df['close']
    m = Prophet(interval_width=0.95)
    m.fit(df_p)
    future = m.make_future_dataframe(periods=7, include_history=True)
    future = future[future['ds'].dt.dayofweek < 5]
    future.tail()
    forecast = m.predict(future)
    fig1 = m.plot(forecast)
    fig1.suptitle(sec)
    fig1.savefig(f'./analytics_images/{sec}_fbprophet.png', dpi=50)
    plt.close('all')
    forecast_past = process_forecast_past(sec, forecast)
    forecast_future = process_forecast_future(sec, forecast)
    return forecast_past, forecast_future


def process_forecast_past(sec, forecast):
    forecast_past = forecast.head(len(forecast) - 5)
    forecast_past = forecast_past.tail(5 * len(cutoffs)).reset_index()
    forecast_past['dt'] = forecast_past['ds'].dt.time
    forecast_past['wd'] = forecast_past['ds'].dt.weekday + 1
    forecast_past['additive_terms'] = forecast_past['additive_terms'] - forecast_past['additive_terms'].mean()
    forecast_past['additive_terms_prct'] = forecast_past['additive_terms'] / forecast_past['trend'] * 100
    forecast_past = forecast_past[['additive_terms', 'wd', 'dt', 'additive_terms_prct']].sort_values(
        ['wd', 'dt']).reset_index(drop=True)
    forecast_past['sec'] = sec
    fig1 = forecast_past.plot(y='additive_terms_prct', title=sec)
    fig = fig1.get_figure()
    fig.savefig(f'./analytics_images/{sec}_weekly.png', dpi=50)
    plt.close('all')
    return forecast_past


def process_forecast_future(sec, forecast):
    forecast_future = forecast.tail(5).reset_index(drop=True)
    forecast_future['sigma'] = (forecast['yhat_upper'] - forecast['yhat_lower']) / forecast['yhat'] / 2
    forecast_future['trend_abs'] = (forecast_future.loc[4, 'trend'] - forecast_future.loc[0, 'trend']) / (
            forecast_future.loc[4, 'ds'] - forecast_future.loc[0, 'ds']).days
    forecast_future['trend_rel_pct'] = forecast_future['trend_abs'] / forecast_future.loc[0, 'trend'] * 100
    forecast_future['sigma'] = forecast_future.loc[0, 'sigma']
    forecast_future.drop(['trend', 'additive_terms'], axis=1, inplace=True)
    forecast_future['sec'] = sec
    forecast_future = forecast_future[
        ['ds', 'yhat_lower', 'yhat_upper', 'yhat', 'sigma', 'trend_abs', 'trend_rel_pct', 'sec']]
    return forecast_future.head(1)


res_past = pd.DataFrame()
res_future = pd.DataFrame()
for ticker in tickers:
    try:
        forecast_past, forecast_future = predict(ticker)
        res_past = pd.concat([res_past, forecast_past], axis=0)
        res_future = pd.concat([res_future, forecast_future], axis=0)
    except Exception as e:
        logger.error(f"{ticker} : {e}")

logger.info(res_future)
sql.get_table.df_to_sql(res_future, 'analytics_future')

logger.info(res_past)
sql.get_table.df_to_sql(res_past, 'analytics_past')


def get_beta(sec, base_asset='CRZ3'):
    xdf = df_pivot[df_pivot['security'] == base_asset][['dtime', 'close']]
    ydf = df_pivot[df_pivot['security'] == sec][['dtime', 'close']]

    df_merged = xdf.merge(ydf, how='inner', on='dtime')
    X = df_merged['close_x'].values.reshape(-1, 1)
    Y = df_merged['close_y'].values.reshape(-1, 1)
    linear_regressor = LinearRegression()
    linear_regressor.fit(X, Y)
    Y_pred = linear_regressor.predict(X)

    beta = round(X[0][0] * linear_regressor.coef_[0][0] / Y[0][0], 2)
    r2 = round(r2_score(Y, Y_pred), 2)

    xfit = np.linspace(min(*X), max(*X), 1000)
    yfit = linear_regressor.predict(xfit)
    plt.clf()
    plt.scatter(X, Y)
    plt.plot(xfit, yfit);
    plt.title(f"{sec} vs {base_asset}: b:{beta} r2:{r2}")
    plt.savefig(f'./analytics_images/{sec}_lr_{base_asset}.png', dpi=50)
    plt.close('all')
    return beta, r2


def build_beta_df():
    result = []
    for sec in df_pivot['security'].unique():
        for base_asset in check_list:
            try:
                beta, r2 = get_beta(sec, base_asset)
                result.append((sec, base_asset, beta, r2))
            except:
                pass
    res = (pd.DataFrame(result, columns=['sec', 'base_asset', 'beta', 'r2']))
    return res


def build_corr():
    res = []
    df = df_pivot.pivot(index='dtime', columns='security', values='close')

    for asset in check_list:
        try:
            next_df = df.corr()[asset].reset_index()
            next_df['base_asset'] = asset
            next_df.columns = ['sec', 'corr', 'base_asset']
            res.append(next_df)
        except:
            pass
    return pd.concat(res, axis=0)


logger.info("building beta")
df_beta = build_beta_df()

logger.info("building corell")
df_corr = build_corr()

logger.info("merging")
df_final = df_beta.merge(df_corr, on=['sec', 'base_asset'])
sql.get_table.df_to_sql(df_final, 'analytics_beta')
logging.info(df_final)

df_news = get_time_cutoff_df(datetime.time(18, 45, 0))
df_news = df_news.sort_values(['security', 'class_code', 'dtime'], ascending=False)
df_news['wd'] = df_news['dt'].apply(lambda x: x.weekday())
df_news = df_news[df_news['wd'] < 5]
df_news = df_news[['close', 'volume', 'security', 'dt']]


start_date = datetime.datetime.combine(min(df_news['dt']), datetime.datetime.min.time())

news_collection = client.trading['news']
news_filter = {"date": {"$gte": start_date}}
res = []
for item in news_collection.find(news_filter):
    for tag in item['tags']:
        res.append((item['_id'], item['channel_title'], item['date'], tag, 1 / len(item['tags'])))

counter = pd.DataFrame(res, columns=['id', 'channel', 'date', 'security', 'weight'])

counter['dt'] = counter['date'].dt.date
counter_df = counter.groupby(['dt', 'security']).sum('weight').reset_index()
df_news = df_news.merge(counter_df, on=['dt', 'security'], how='left')
df_news['dt'] = df_news['dt'].apply(lambda x: datetime.datetime.combine(x, datetime.datetime.min.time()))
df_news = df_news.fillna(0)
df_news.sort_values(['security', 'dt'])


def plot_news(sec):
    df_tmp = df_news[df_news['security'] == sec]
    if len(df_tmp) == 0: return
    fig, ax1 = plt.subplots()
    fig.set_figwidth(20)
    ax2 = ax1.twinx()
    max_vol = max(df_tmp['volume'])
    max_weight = max(df_tmp['weight'])

    width = datetime.timedelta(hours=6)

    ax1.plot(df_tmp['dt'], df_tmp['close'], color='b')
    ax2.bar(df_tmp['dt'] - width, df_tmp['volume'] / max_vol * max_weight, color='yellow', align='center', width=0.2)
    ax2.bar(df_tmp['dt'], df_tmp['weight'], color='red', align='center', width=0.2)
    ax2.xaxis_date()
    fig.autofmt_xdate(rotation=90)
    plt.savefig(f'./analytics_images/{sec}_vols.png', dpi=50)
    plt.close('all')


for ticker in tickers:
    plot_news(ticker)

exec(open("balance_orders.py").read())
#subprocess.run(["python", "balance_orders.py"])