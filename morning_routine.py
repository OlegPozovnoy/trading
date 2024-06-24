import asyncio
import json
import logging
import os
import sys
import time
import datetime
import traceback

import pandas as pd
from dotenv import load_dotenv, find_dotenv

import sql.get_table
import sql.async_exec
import subprocess

from nlp.mongo_tools import clean_mongo
from tinkoff_candles import import_new_tickers
from tools.utils import sync_timed, async_timed

load_dotenv(find_dotenv('my.env', True))
engine = sql.get_table.engine
settings_path = os.environ['instrument_list_path']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@sync_timed()
def calc_bollinger(end_cutoff=datetime.time(17, 45, 0)):
    """
    df_bollinger: Calculate and store bollinger
    df_volumes: Calc avg+3*std volumes (rolling 10 mins). Error, df_volumes should be from full dataset
    :param end_cutoff: bollinger quotes time
    :return:
    """
    df_ = sql.get_table.load_candles_cutoff([end_cutoff])
    df_['t'] = pd.to_datetime(df_['datetime'], format='%d.%m.%Y %H:%M')
    df_['dt'] = df_['t'].dt.date
    df_['time'] = df_['t'].dt.time

    # get last close
    df_bollinger = df_[df_['time'] <= end_cutoff] \
        .sort_values(['security', 'class_code', 'dt', 'time'], ascending=False) \
        .groupby(['security', 'class_code', 'dt']) \
        .head(1) \
        .reset_index()

    # get last 20 values
    df_bollinger = df_bollinger \
        .sort_values(['security', 'class_code', 'dt'], ascending=False) \
        .groupby(['security', 'class_code']) \
        .head(20) \
        .reset_index()

    # calc
    df_bollinger = df_bollinger \
        .groupby(['security', 'class_code']) \
        .agg(mean=('close', 'mean'), std=('close', 'std'), count=('close', 'count')) \
        .reset_index()

    # custom cols
    df_bollinger['prct'] = df_bollinger['std'] / df_bollinger['mean']
    df_bollinger['up'] = df_bollinger['std'] * 2 + df_bollinger['mean']
    df_bollinger['down'] = -df_bollinger['std'] * 2 + df_bollinger['mean']

    # save
    sql.get_table.exec_query("delete from public.df_bollinger")
    df_bollinger.to_sql('df_bollinger', engine, if_exists='append')


@sync_timed()
def calc_volumes():
    """
    updates df_volumes: all avg std smoothed by 10 mins to get jumps
    :return:
    """
    volumes_query = """
    TRUNCATE TABLE df_volumes;
    insert into df_volumes
    (with t_main as 
    (
	SELECT close, 
	close - lag(close, 1) OVER (PARTITION BY security ORDER BY datetime) AS diff,
	(close - lag(close, 1) OVER (PARTITION BY security ORDER BY datetime))/close as diff_prct,
	volume, security, class_code, datetime,
	CURRENT_DATE + datetime::time without time zone AS tm,
    EXTRACT(dow FROM datetime)::text AS wd,
	close*volume as money_volume,
	date(datetime) as dt
	FROM public.df_all_candles_t
	where
	EXTRACT(dow FROM datetime) <> ALL (ARRAY[0::numeric, 6::numeric])
	and datetime < CURRENT_DATE
	and class_code <> 'TQPI'
    )
    select 
	t1.security,
	t1.class_code, 
	t1.tm, 
	t1.points_num,
	
	t1.volume_std*t1.points_num/t2.cnt_days as volume_std,
	avg(volume_std*t2.cnt_days/t1.points_num) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as volume_std_10,
	
	t1.volume/t2.cnt_days as volume_avg, 
	avg(t1.volume/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as volume_avg_10,	
	
	t1.money_volume/t2.cnt_days as money_volume_avg,
	avg(t1.money_volume/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as money_volume_avg_10,	
	
	t1.diff_mean*t1.points_num/t2.cnt_days as diff_mean,
	avg(t1.diff_mean*t1.points_num/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as diff_mean_10,	
	
	t1.diff_std*t1.points_num/t2.cnt_days as diff_std,
	avg(t1.diff_std*t1.points_num/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as diff_std_10,	

	t1.diff_prct_mean*t1.points_num/t2.cnt_days as diff_prct_mean,
	avg(t1.diff_prct_mean*t1.points_num/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as diff_prct_mean_10,	
	
	t1.diff_prct_std*t1.points_num/t2.cnt_days as diff_prct_std,
	avg(t1.diff_prct_std*t1.points_num/t2.cnt_days) over (partition by t1.security order by t1.tm asc 
	rows BETWEEN 9 PRECEDING and current row) as diff_prct_std_10,	
	
	t2.cnt_days,
	t2.max_dt,
	t2.max_datetime,
	t_close.close,
	coalesce(volume_last, 0) as volume_last,
	coalesce(money_volume_last, 0) as money_volume_last
	from
    (select security, class_code, tm, sum(volume) as volume, sum(money_volume) as money_volume, 
	count(*) as points_num, STDDEV(volume) as volume_std, 
	avg(diff) as diff_mean, STDDEV(diff) as diff_std, 
	avg(diff_prct) as diff_prct_mean, STDDEV(diff_prct) as diff_prct_std 
	from t_main 
	group by security, class_code, tm) 
	as t1
    left join
    (
    select security, class_code, count(distinct dt) as cnt_days, max(dt) as max_dt, max(datetime) as max_datetime from t_main
    group by security,class_code) 
        as t2
    on t1.security = t2.security 
    left join
    (select security, class_code, close, datetime from t_main) as t_close
    on t1.security = t_close.security 
        and t2.max_datetime = t_close.datetime
    left join
    (select security, class_code, tm,dt, volume as volume_last, volume*close as money_volume_last from t_main) 
        as t_lastvol
    on t1.security = t_lastvol.security 
        and t2.max_dt = t_lastvol.dt
        and t1.tm = t_lastvol.tm
	)
    """
    sql.get_table.exec_query(volumes_query)


def calc_report_minmax():
    """
    report on minmax dynamics
    :return:
    """
    query = """
        TRUNCATE TABLE public.report_minmax;
        insert into public.report_minmax
        select security, date(datetime),  
        (max(close) - min(close)) as min_max, 
        max(high) - min(low) as high_low,
        (max(close) - min(close))/avg(close) as min_max_prct
        from df_all_candles_t
        group by security, date(datetime)
    """
    sql.get_table.exec_query(query)


def calc_report_deal_imp_arch():
    """
    report on minmax dynamics
    :return:
    """
    query = """
        TRUNCATE TABLE public.report_deal_imp_arch_t;
        insert into public.report_deal_imp_arch_t
         SELECT tradedate + "time" AS datetime,
            code,
            price,
            sum(
                CASE
                    WHEN bs::text = 'BUY'::text THEN 1
                    WHEN bs::text = 'SELL'::text THEN '-1'::integer
                    ELSE 0
                END * amount) AS net_amount,
            sum(amount) AS total_amount,
            avg(open_interest) AS avg_open_interest
           FROM deals_imp_arch
          GROUP BY code, (tradedate + "time"), bs, price
          ORDER BY code, (tradedate + "time") DESC;
    """
    sql.get_table.exec_query(query)


@sync_timed()
def move_diff_to_arch():
    """
    to speedup daily selects, we move [sec,fut]quotesdiffhist to [sec,fut]quotesdiffhist_arch
    :return:
    """
    for prefix in ['sec', 'fut']:
        query = f"""
        insert into {prefix}quotesdiffhist_arch
        select * from {prefix}quotesdiffhist where last_upd < CURRENT_DATE;
        DELETE from {prefix}quotesdiffhist where last_upd < CURRENT_DATE;
        """
        sql.get_table.exec_query(query)


@async_timed()
async def clean_db():
    fut_postfix = os.environ['futpostfix']
    move_diff_to_arch()

    sql_query_list = [
        "DELETE	FROM public.secquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);",
        "DELETE	FROM public.futquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);",
        "DELETE FROM public.df_all_candles_t_arch WHERE datetime < now() - interval '90 days'",
        "DELETE FROM public.deals_imp_t",
        #"DELETE FROM public.futquotesdiffhist 	where updated_at < (CURRENT_DATE-14);",
        "DELETE FROM public.futquotesdiffhist_arch 	where updated_at < (CURRENT_DATE-14);",
        #"DELETE FROM public.secquotesdiffhist 	where updated_at < (CURRENT_DATE-14);",
        "DELETE FROM public.secquotesdiffhist_arch 	where updated_at < (CURRENT_DATE-14);",
        "DELETE FROM public.events_jumps_hist where  updated_at < (CURRENT_DATE-14);",
        "DELETE FROM public.order_discovery;",
        "DELETE FROM public.deals_ba_hist 	where updated_at < (CURRENT_DATE-14);",
        "DELETE	FROM public.secquotes where updated_at < (CURRENT_DATE-1);",
        #"DELETE	FROM public.secquotes;",
        "DELETE	FROM public.futquotes where updated_at < (CURRENT_DATE-1);",
        "DELETE FROM public.orders_in;",
        "DELETE FROM public.orders_out;",
        "DELETE FROM public.orders_in_tcs;",
        "DELETE FROM public.orders_out_tcs;",
        "DELETE	FROM public.pos_eq;",
        "DELETE	FROM public.pos_collat;",
        "DELETE	FROM public.deals;",
        "DELETE	FROM public.deorders;",
        "DELETE	FROM public.df_monitor;",
        f"delete FROM public.futquotesdiff where right(code,2) <> '{fut_postfix}'",
        "insert into deals_imp_arch select * from deals_imp on conflict (deal_id,tradedate) do nothing",
        "insert into deals_myhist select * from deals on conflict (deal_id,tradedate) do nothing"
    ]
    await sql.async_exec.exec_list(sql_query_list)
    print("bulk of queries is executed")
    query = """
        WITH moved_rows AS (
            DELETE FROM df_all_candles_t  a
            WHERE datetime < now() - interval '28 days'
            RETURNING a.* -- or specify columns
        )
        INSERT INTO df_all_candles_t_arch  --specify columns if necessary
        SELECT  * FROM moved_rows;    
    """
    engine.execute(query)

    query = """
    insert into public.futprefix
    SELECT substr(name, 1, position('-' in name) - 1) as ticker, 
	substr(ticker, 1, length(ticker) - 2) as futprefix
	FROM public.tinkoff_params where 
	class_code = 'SPBFUT'
	and position('-' in name) > 0
	and RIGHT(ticker, 1) ~ '^\d$'
    on conflict (futprefix) do nothing;
    """
    engine.execute(query)


def update_instrument_list(update_sec=True) -> None:
    """
    save futquotes secquotes tables instruments to settings json
    :param update_sec: False if we set equities empty
    :return: None
    """
    setting = {'equities': {}, 'futures': {}}
    setting['equities']['classCode'] = "TQBR"
    setting['futures']['classCode'] = "SPBFUT"

    query_fut = "select distinct code from public.futquotes"
    query_sec = "select distinct code from public.secquotes"

    setting['futures']['secCodes'] = [x[0] for x in sql.get_table.exec_query(query_fut)]
    setting['equities']['secCodes'] = [x[0] for x in sql.get_table.exec_query(query_sec)] if update_sec else []

    if len(setting['futures']['secCodes']) + len(setting['equities']['secCodes']) == 0:
        logger.error("cant update instruments: fut&secquotes are empty")
        return

    settings_str = json.dumps(setting, indent=4)
    with open(settings_path, "w") as fp:
        fp.write(settings_str)
    print("instrument to import: ", settings_str)


if __name__ == '__main__':
    startTime = time.time()
    try:
        logger.info('Update import settings')
        update_instrument_list()
        logger.info('Begin quotes reimport')
        asyncio.run(import_new_tickers(False))
        logger.info('Bars updated')
        asyncio.run(clean_db())
        logger.info('DB Cleaned')
        clean_mongo()
        logger.info("Mongodb duplicates removed")
        calc_bollinger()
        logger.info('Bollinger recomputed')
        calc_volumes()
        logger.info('volumes updated')
        calc_report_minmax()
        calc_report_deal_imp_arch()
        logger.info('report_minmax updated')
        exec(open("morning_reports.py").read())
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        print(datetime.datetime.now())
