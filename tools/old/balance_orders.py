import sql.get_table
import pandas as pd
import numpy as np
import random
import string

# pos millions
pd.set_option('display.max_columns', None)

engine = sql.get_table.engine

cash_part = 0
k_up = 2
k_down = 4

default_state = 1

# pos_invested, invest_at_bottom, invest_at_top
# тут только фьючи
# Переделать
# 1)сколько я хочу 2) само плечо 3) процент плеча


target_pos = [
    ('ALM4', 15.2, 0.01, 0.99),
    ('CRM4', 27.6, 5.5, 0.5),
    ('GZM4', 5.4, 3.6, 0.5),
    ('LKM4', 3.8, 3, 0.99),
    ('NMM4', -4.4, 5.3, 0),
    ('RLM4', 4.2, 3.8, 0.99),
    ('SRM4', 2, 3.8, 0.99),
    ('SRU4', 9, 3.8, 0.99),
    ('SSM4', 3.5, 3.8, 0.99),
]


def create_initial_dataframe(positions):
    """Создание начального DataFrame на основе списка позиций."""
    df = pd.DataFrame(positions, columns=['code', 'target_exposure', 'k_down', 'k_up'])
    total_volume = df['target_exposure'].abs().sum()
    df['vol'] = df['target_exposure'] / total_volume
    return df


def merge_with_current_positions(df):
    """Объединение DataFrame с текущими позициями из базы данных."""
    current_pos_query = "SELECT code, pos, volume FROM public.united_pos"
    current_pos = sql.get_table.query_to_df(current_pos_query)
    df = df.merge(current_pos, how='left', on='code')
    df[['pos', 'volume']] = df[['pos', 'volume']].fillna(0)
    df['k_down'] = df['k_down'].fillna(k_down)
    df['k_up'] = df['k_up'].fillna(k_up)
    return df


def merge_with_futures_details(df):
    query = """
    select fq.code, leverage*coalesce(multiplier,1) as leverage, collateral, price, ds as snapshot_date, 
    yhat_lower, yhat_upper,yhat, sigma, trend_rel_pct, coalesce(multiplier,1) as multiplier 
    from
    (SELECT code, bid/collateral as leverage, collateral, (bid+ask)/2 as price from public.futquotes) fq
    inner join 
    (SELECT  * FROM public.analytics_future) af
    on fq.code = af.sec
    left join
    public.pos_volmult on left(fq.code,2) = pos_volmult.code
    """
    df_data = sql.get_table.query_to_df(query)
    df = df.merge(df_data, how='inner', on='code')
    return df


df = create_initial_dataframe(target_pos)
df = merge_with_current_positions(df)
df['sid'] = df.apply(lambda x: ''.join(random.choices(string.ascii_uppercase, k=3)), axis=1)
df = merge_with_futures_details(df)

print(df)


def calculate_adjustments_old(df):
    """Расчет корректировок и целевых позиций."""
    global cash_part

    # насколько близко к границе перекупленности-перепроданности (-1,1)
    df['minmax'] = (df['price'] - df['yhat']) / (df['yhat'] - df['yhat_lower'])

    # какой обьем был бы у позиции если бы цена спустилась на границу не в нашу сторону, подходит и для отрицательных позиций
    df['volume_adjusted'] = (abs(df['volume']) *
                             ((df['yhat_lower'] * (df['vol'] > 0)) + (df['yhat_upper'] * (df['vol'] <= 0)))
                             / df['price'] * np.sign(df['vol']))

    # Изменение кша у нас при таком сценарии
    df['money_adjustment'] = np.sign(df['pos']) * np.sign(df['vol']) * df['volume_adjusted'] - df['volume']

    # считываем сколько у нас денег и аджасти если надо
    money = sql.get_table.query_to_list("SELECT pos_current + pos_plan + pnl as money FROM public.pos_money")[0][
        'money']
    money_adjusted = money * (1 - cash_part) + sum(df['money_adjustment'])

    # считаем целевой обьем позиции: раскидали остаток денег пропорционально обьему и умножили на плечо из настроек
    df['target_volume'] = money_adjusted * df['k_down'] * df['vol']

    # считаем сколько будет контрактов по каждой позиции при таком сценарии
    df['target_pos'] = (df['target_volume'] /
                        (df['yhat_lower'] * (df['vol'] > 0) + df['yhat_upper'] * (df['vol'] <= 0))
                        / df['multiplier'])

    # считаем позицию при сценарии когда цена дошла до верха коридора (то есть сколько надо продать)
    df['target_pos_neutral'] = df['target_pos'] / df['k_down'] * df['k_up']

    # для инфо текущий K.
    df['current_k'] = df['pos'] / df['target_pos'] * df['k_down']

    # чтобы в csv была колонка справа
    df['code2'] = df['code']
    return df


df = calculate_adjustments_old(df)
df.to_csv('balance_pos.csv', sep='\t')

engine.execute("delete from public.orders_my where comment like 'BAL%%'")

for idx, row in df.iterrows():
    # участок кода для сокращения позиции при приближении к профиту
    # используются колонки ['current_k','k_up', 'k_down', направление позиции], остальное не расчитывается

    # если есть что продавать
    if row['current_k'] > row['k_up']:

        current_k = min(row['current_k'], row['k_down'])
        quantity = int(row['target_pos_neutral'] - row['pos'])

        if row['vol'] > 0:  # позиция лонг - мы ее закрываем
            # начинаем закрывать позицию разбивая отрезок [yhat_upper-std/3; yhat_upper] пропорционально уже закрытой части
            barrier = (row['yhat_upper'] - (row['yhat_upper'] - row['yhat']) / 3
                       * (current_k - row['k_up']) / (row['k_down'] - row['k_up']))

            barrier_bound = row['yhat_upper']

        else:  # позиция шорт, мы ее закрываем
            # начинаем закрывать позицию разбивая отрезок [yhat_lower; yhat_lower+std/3] пропорционально уже закрытой части
            barrier = (row['yhat_lower'] + (row['yhat'] - row['yhat_lower']) / 3
                       * (current_k - row['k_up']) / (row['k_down'] - row['k_up']))

            barrier_bound = row['yhat_lower']

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values({default_state}, {quantity}, 'BAL_UP_{row['code']}_{row['sid']}',0,{barrier},1,10,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)

    # участок кода для увеличения позиции при приближении к лосям
    # если можно еще купить
    if row['current_k'] < row['k_down']:

        current_k = max(row['current_k'], row['k_up'])
        quantity = int(row['target_pos'] - row['pos'])

        if row['vol'] > 0:  # увеличение позиции = buy
            # начинаем закрывать позицию разбивая отрезок [yhat_lower; yhat_lower+std/3] пропорционально уже закрытой части
            barrier = (row['yhat_lower'] + (row['yhat'] - row['yhat_lower']) / 3
                       * (row['k_down'] - current_k) / (row['k_down'] - row['k_up']))

            barrier_bound = row['yhat_lower']

        else:  # увеличение позиции = sell
            # начинаем закрывать позицию разбивая отрезок [yhat_upper-std/3; yhat_upper] пропорционально уже закрытой части
            barrier = (row['yhat_upper'] - (row['yhat_upper'] - row['yhat']) / 3
                       * (row['k_down'] - current_k) / (row['k_down'] - row['k_up']))

            barrier_bound = row['yhat_upper']

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values({default_state}, {quantity}, 'BAL_DOWN_{row['code']}_{row['sid']}',0,{barrier},1,10,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)
