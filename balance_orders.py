import sql.get_table
import pandas as pd
import random
import string

pd.set_option('display.max_columns', None)
engine = sql.get_table.engine

# 1)сколько я хочу млн 2) процент плеча

default_state = 0
desired_pos = [
    ('ALU4', 12, 0.75),
    ('MXU4', 1, 0.99),
    ('SSU4', 4, 0.99),
]


def create_initial_dataframe(positions):
    """Создание начального DataFrame на основе списка позиций."""
    df = pd.DataFrame(positions, columns=['code', 'target_volume', 'part_to_keep'])
    df['target_volume'] *= 1_000_000
    return df


def merge_with_current_positions(df):
    """Объединение DataFrame с текущими позициями из базы данных."""
    current_pos_query = "SELECT code, pos, volume FROM public.united_pos"
    current_pos = sql.get_table.query_to_df(current_pos_query)
    df = df.merge(current_pos, how='left', on='code')
    df[['pos', 'volume']] = df[['pos', 'volume']].fillna(0)
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


def intermediate_calc(df):
    """мэппинг старой версии колонок на новую"""
    df['k_down'] = df['leverage']
    df['k_up'] = df['k_down'] * df['part_to_keep']
    # добавим интересные колонки
    df['cur_collateral'] = df['pos'].abs() * df['collateral']
    # паузу в ордерах для CR ставим 1 для остальных 10
    df['pause'] = df['code'].apply(lambda x: 1 if x[:2] == 'CR' else 10)
    return df


df = create_initial_dataframe(desired_pos)
df = merge_with_current_positions(df)
df['sid'] = df.apply(lambda x: ''.join(random.choices(string.ascii_uppercase, k=3)), axis=1)
df = merge_with_futures_details(df)
df = intermediate_calc(df)


def calculate_adjustments(df):
    """Расчет корректировок и целевых позиций."""
    # насколько близко к границе перекупленности-перепроданности (-1,1)
    df['minmax'] = (df['price'] - df['yhat']) / (df['yhat'] - df['yhat_lower'])

    # считаем позицию исходя из мида yhat
    df['target_pos'] = df['target_volume'] / (df['yhat'] * df['multiplier'])

    # считаем позицию при сценарии когда цена дошла до верха коридора (то есть сколько надо продать)
    df['target_pos_neutral'] = df['target_pos'] / df['k_down'] * df['k_up']

    # для инфо текущий K.
    df['current_k'] = df['pos'] / df['target_pos'] * df['k_down']

    # чтобы в csv была колонка справа
    df['code2'] = df['code']
    return df


df = calculate_adjustments(df)
df.to_csv('balance_pos.csv', sep='\t')

engine.execute("delete from public.orders_my where comment like 'BAL%%'")

for idx, row in df.iterrows():
    # участок кода для сокращения позиции при приближении к профиту
    # используются колонки ['current_k','k_up', 'k_down', направление позиции], остальное не расчитывается

    # если есть что продавать
    if row['current_k'] > row['k_up']:

        current_k = min(row['current_k'], row['k_down'])
        quantity = int(row['target_pos_neutral'] - row['pos'])

        if row['target_volume'] > 0:  # позиция лонг - мы ее закрываем
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
                    values({default_state}, {quantity}, 'BAL_UP_{row['code']}_{row['sid']}',0,{barrier},1,{row['pause']},'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)

    # участок кода для увеличения позиции при приближении к лосям
    # если можно еще купить
    if row['current_k'] < row['k_down']:

        current_k = max(row['current_k'], row['k_up'])
        quantity = int(row['target_pos'] - row['pos'])

        if row['target_volume'] > 0:  # увеличение позиции = buy
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
                    values({default_state}, {quantity}, 'BAL_DOWN_{row['code']}_{row['sid']}',0,{barrier},1,{row['pause']},'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)
