import sql.get_table
import pandas as pd
import numpy as np
import random
import string

# pos millions

engine = sql.get_table.engine

cash_part = 0
k_up = 3
k_down = 5

target_pos = [
    ('SRZ3', 25, 5, 3),
    ('MXZ3', 25),
    ('VBZ3', 3),

    ('MNZ3', 0.1),

    ('LKZ3', 0.1),
    ('RNZ3', 0.1),
    ('GZZ3', 0.1),

    ('MGZ3', 10),
    ('CHZ3', 5),

    ('ALZ3', 3)
]

df = pd.DataFrame(target_pos, index=range(len(target_pos)), columns=['code', 'vol', 'k_down', 'k_up'])
df['vol'] = df['vol'] / sum([abs(v[1]) for v in target_pos])

current_pos = sql.get_table.query_to_df("SELECT code, pos, volume FROM public.united_pos")
df = df.merge(current_pos, how='left', on='code')
df[['pos', 'volume']] = df[['pos', 'volume']].fillna(0)
df['k_down'] = df['k_down'].fillna(k_down)
df['k_up'] = df['k_up'].fillna(k_up)
df['sid'] = df.apply(lambda x: ''.join(random.choices(string.ascii_uppercase, k=3)), axis=1)
query = """
select code, leverage, collateral, price, ds as snapshot_date, yhat_lower, yhat_upper,yhat, sigma, trend_rel_pct from
(SELECT code, bid/collateral as leverage, collateral, (bid+ask)/2 as price from futquotes) fq
inner join 
(SELECT  * FROM public.analytics_future) af
on fq.code = af.sec

"""
df_data = sql.get_table.query_to_df(query)
df = df.merge(df_data, how='inner', on='code')
df['minmax'] = (df['price'] - df['yhat']) / (df['yhat'] - df['yhat_lower'])
df['volume_adjusted'] = abs(df['volume']) * (df['yhat_lower'] * (df['vol'] > 0) + df['yhat_upper'] * (df['vol'] <= 0)) / \
                        df['price'] * np.sign(df['vol'])

df['money_adjustment'] = np.sign(df['pos']) * np.sign(df['vol']) * df['volume_adjusted'] - df['volume']
money = sql.get_table.query_to_list("SELECT pos_current + pos_plan + pnl as money FROM public.pos_money")[0]['money']

# сколько б у нас было денег если бы все ушло в неблагоприятную сторону
money_adjusted = money * (1 - cash_part) + sum(df['money_adjustment'])

df['target_volume'] = money_adjusted * df['k_down'] * df['vol']
df['target_pos'] = df['target_volume'] / (df['yhat_lower'] * (df['vol'] > 0) + df['yhat_upper'] * (df['vol'] <= 0))/df['volume'] * df['price'] * df['pos']
df['target_pos_neutral'] = df['target_pos'] / df['k_down'] * df['k_up']
df['current_k'] = df['pos'] / df['target_pos'] * df['k_down']
df['code2'] = df['code']
df.to_csv('balance_pos.csv', sep='\t')

engine.execute("delete from public.orders_my where comment like 'BAL%%'")

for idx, row in df.iterrows():
    # если мы можем еще закрывать позицию при приближении к профиту
    if row['current_k'] > row['k_up']:
        current_k = min(row['current_k'], row['k_down'])

        quantity = int(row['target_pos_neutral'] - row['pos'])

        if row['vol'] > 0:  # уменьшение позиции = sell
            barrier = row['yhat_upper'] - (row['yhat_upper'] - row['yhat']) / 2 * (current_k - row['k_up']) / (
                        row['k_down'] - row['k_up'])

            barrier_bound = row['yhat_upper']

        else:  # уменьшение позиции = buy
            barrier = row['yhat_lower'] + (row['yhat'] - row['yhat_lower']) / 2 * (current_k - row['k_up']) / (
                        row['k_down'] - row['k_up'])

            barrier_bound = row['yhat_lower']

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values(1,{quantity}, 'BAL_UP_{row['code']}_{row['sid']}',0,{barrier},1,5,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)

    # если мы можем еще открывать позицию при приближении к лосям
    if row['current_k'] < row['k_down']:
        current_k = max(row['current_k'], row['k_up'])

        quantity = int(row['target_pos'] - row['pos'])

        if row['vol'] > 0:  # увеличение позиции = buy
            barrier = row['yhat_lower'] + (row['yhat'] - row['yhat_lower']) / 2 * (row['k_down'] - current_k) / (
                        row['k_down'] - row['k_up'])

            barrier_bound = row['yhat_lower']

        else:  # увеличение позиции = sell
            barrier = row['yhat_upper'] - (row['yhat_upper'] - row['yhat']) / 2 * (row['k_down'] - current_k) / (
                        row['k_down'] - row['k_up'])

            barrier_bound = row['yhat_upper']

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values(1,{quantity}, 'BAL_DOWN_{row['code']}_{row['sid']}',0,{barrier},1,5,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)