import sql.get_table
from monitor import logger, send_df
from tools.utils import sync_timed
import pandas as pd


@sync_timed()
def monitor_gains_main(urgent_list):
    df_gains_10 = get_all_gains(10)
    df_gains_540 = get_all_gains(540)

    df_thr, df_top5 = get_filtered_gains(df_gains_10, threshold=0.5)
    df_volumes = get_volumes_df(df_gains_10, df_gains_540, urgent_list, mins_lookback=10, daily_lookback=540, days_lookback=14)
    print('df_volumes', df_volumes.columns)

    df_top5['close_x'] = df_top5['close_x'].astype(str).replace(r'0+$', '', regex=True)
    send_df(df_top5)

    df_volumes_highstd = df_volumes[df_volumes['std'] > 2]
    send_df(format_volumes(df_volumes_highstd[df_volumes_highstd['security'].isin(urgent_list)]), True)
    send_df(format_volumes(df_volumes_highstd), False)

    send_df(format_jumps(df_thr[df_thr['security'].isin(urgent_list)]), True)
    send_df(format_jumps(df_thr), False)

    df_volumes_highstd = df_volumes_highstd[df_volumes_highstd["timeframe"] == 'mins']
    return pd.concat(
        [df_volumes_highstd['security'], df_thr['security']]).drop_duplicates(), df_volumes


@sync_timed()
def get_volumes_df(df_inc_mins, df_inc_days, urgent_list, mins_lookback=10, daily_lookback=540, days_lookback=14):
    # 540 это -9 часов, чтобы это сработало в 9 утра
    def get_abnormal_volumes(urgent_list, minutes_lookback, days_lookback=days_lookback):
        urgent_filter = "OR cur.security in ('" + "','".join(urgent_list) + "')"
        query = f"""
        WITH t_main AS (
            SELECT security, DATE(datetime) AS dt, SUM(volume) AS volume
            FROM public.df_all_candles_t
            WHERE 
                EXTRACT(DOW FROM datetime) <> ALL (ARRAY[0::numeric, 6::numeric])
                AND class_code <> 'TQPI'
                AND CURRENT_DATE + datetime::time WITHOUT TIME ZONE BETWEEN NOW() - INTERVAL '{minutes_lookback} minutes' and NOW()
                AND CURRENT_DATE - {days_lookback} <= DATE(datetime)
            GROUP BY security, DATE(datetime)
        )
        SELECT cur.security, volume_mean, points_num, volume_std, volume,
            (volume - volume_mean) / volume_std AS std 
        FROM (
            SELECT security, AVG(volume) AS volume_mean, COUNT(DISTINCT dt) AS points_num, STDDEV(volume) AS volume_std
            FROM t_main
            WHERE dt < CURRENT_DATE
            GROUP BY security
            HAVING STDDEV(volume) > 0
        ) hist
        INNER JOIN 
        (SELECT security, volume 
            FROM t_main
            WHERE dt = CURRENT_DATE
        ) cur
        ON hist.security = cur.security
        WHERE (volume - volume_mean) / volume_std > 2
        {urgent_filter}
        order by std desc;
        """
        return sql.get_table.query_to_df(query)

    df_minutes = get_abnormal_volumes(urgent_list, mins_lookback, days_lookback)
    print('df_minutes', df_minutes.columns)
    print('df_inc_mins', df_inc_mins.columns)
    if len(df_minutes) > 0:
        df_minutes = df_minutes.merge(df_inc_mins[['security', 'inc', 'base_inc', 'beta', 'r2']], how='left',
                                      on='security')
    df_minutes['timeframe'] = 'mins'

    df_daily = get_abnormal_volumes(urgent_list, daily_lookback, days_lookback)
    print('df_daily', df_daily.columns)
    print('df_inc_days', df_inc_days.columns)
    if len(df_daily) > 0:
        df_daily = df_daily.merge(df_inc_days[['security', 'inc', 'base_inc', 'beta', 'r2']], how='left', on='security')
    df_daily['timeframe'] = 'days'

    return pd.concat([df_minutes, df_daily], axis=0).reset_index()


@sync_timed()
def get_all_gains(min_lag, base_asset='MXM4'):
    """
    возвращаем то чот выросло нв трешхолд процентов за минлаг минут
    :param min_lag: minutes
    :param base_asset: betas calc
    :return:
    """

    query = f"""
    SELECT 
    x.security, x.class_code, x.close_x, y.close_y, x.cdate_x, y.cdate_y,
    (x.close_x / y.close_y - 1) * 100 AS inc,
    beta.beta, beta.r2, beta.corr, beta.base_asset
    FROM
    (SELECT security, class_code, close AS close_x, datetime AS cdate_x
    FROM
        (SELECT *, ROW_NUMBER() OVER (PARTITION BY security ORDER BY datetime DESC) AS rownb
        FROM df_all_candles_t
        WHERE datetime > NOW() - INTERVAL '3 days') latest_candles
    WHERE rownb = 1) x 
    INNER JOIN
    (SELECT security, close AS close_y, datetime AS cdate_y
    FROM
        (SELECT *, ROW_NUMBER() OVER (PARTITION BY security ORDER BY datetime DESC) AS rownb
        FROM df_all_candles_t
        WHERE datetime > NOW() - INTERVAL '3 days' 
        AND datetime < NOW() - INTERVAL '{min_lag} minutes') latest_candles
    WHERE rownb = 1) y 
    ON x.security = y.security
    LEFT JOIN
    (SELECT sec, beta, r2, corr, base_asset
    FROM public.analytics_beta
    WHERE base_asset = '{base_asset}') beta
    ON x.security = beta.sec;
    """

    df = sql.get_table.query_to_df(query)
    base_inc = df[df['security'] == base_asset]['inc'].iloc[0]
    df['base_inc'] = base_inc
    return df


@sync_timed()
def get_filtered_gains(df_res, threshold=0.5):
    df_fut = df_res[df_res['class_code'] == 'SPBFUT'].sort_values('inc').reset_index()
    df_eq = df_res[df_res['class_code'] != 'SPBFUT'].sort_values('inc').reset_index()

    df_inc = pd.concat([df_eq.head(5), df_eq.tail(5), df_fut.head(5), df_fut.tail(5)])[
        ['security', 'inc', 'close_x', 'cdate_x']] \
        .sort_values('inc').reset_index(drop=True)

    df_inc['cdate_x'] = df_inc['cdate_x'].apply(lambda x: x.strftime("%H:%M"))
    df_inc['inc'] = df_inc['inc'].round(2)
    logger.info(f"full df inc\n {df_inc}")
    return df_res[(df_res['inc'] >= threshold) | (df_res['inc'] <= -threshold)], df_inc


def format_volumes(df):
    for col in ['std', 'beta']:
        df[col] = df[col].astype(float).round(1)

    for col in ['volume_mean', 'volume_std', 'volume']:
        df[col] = df[col].astype(int)

    for col in ['inc', 'base_inc', 'beta', 'r2']:
        df[col] = df[col].astype(float).round(2)

    return df[['security', 'std', 'timeframe', 'volume_mean', 'volume_std', 'inc', 'beta', 'base_inc', 'r2']]


def format_jumps(df):
    df['cdate_x'] = df['cdate_x'].dt.strftime("%H:%M")
    df['inc'] = df['inc'].astype(float).round(2)
    df['close_x'] = df['close_x'].astype(float).round(4)
    return df[['security', 'inc', 'close_x', 'cdate_x', 'base_inc', 'beta', 'r2']]
