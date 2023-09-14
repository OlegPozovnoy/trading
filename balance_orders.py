import sql.get_table
import pandas as pd
#pos millions

engine=sql.get_table.engine

engine.execute("delete from public.orders_my where comment like 'BAL%%'")

k_up = 0
k_down = 2

target_pos = [
('SRU3', 20),
('LKZ3', 6),
('RNU3', 5.5),
('MGZ3', 10),
('NMZ3', 5.5),
('MNU3', 13)
]

df = pd.DataFrame(target_pos, index = range(len(target_pos)), columns=['code','vol'])
df['vol'] = df['vol']/sum([v[1] for v in target_pos])

current_pos = sql.get_table.query_to_df("SELECT code, pos, volume FROM public.united_pos")
df = df.merge(current_pos, how='inner', on = 'code')
df = df.fillna(0)


query = """
select code, leverage, collateral, price, ds, yhat_lower, yhat_upper,yhat, sigma, trend_rel_pct from
(SELECT code, bid/collateral as leverage, collateral, (bid+ask)/2 as price from futquotes) fq
inner join 
(SELECT  * FROM public.analytics_future) af
on fq.code = af.sec

"""
df_data = sql.get_table.query_to_df(query)
df = df.merge(df_data, how='inner', on='code')
df['minmax'] = (df['price']-df['yhat'])/(df['yhat']-df['yhat_lower'])
df['volume_adjusted'] = df['volume'] * (df['yhat_lower']/df['price'])
df['money_adjustment'] = df['volume_adjusted'] - df['volume']
money = sql.get_table.query_to_list("SELECT pos_current + pos_plan + pnl as money FROM public.pos_money")[0]['money']
money_adjusted = money+sum(df['money_adjustment'])

df['k_down'] = k_down
df['k_up'] = k_up

df['target_volume'] = money_adjusted * df['k_down'] * df['vol']
df['target_pos'] = df['target_volume']/ df['yhat_lower']
df['target_pos_neutral'] = df['target_pos']/df['k_down'] * df['k_up']
df['current_k'] = df['pos']/df['target_pos'] * df['k_down']
df.to_csv('balance_pos.csv', sep = '\t')

for idx, row in df.iterrows():
    if row['current_k'] > k_up:
        current_k = min(row['current_k'], k_down)
        quantity = int(row['target_pos_neutral'] - row['pos'])
        barrier_bound = row['yhat_upper']
        barrier = row['yhat_upper'] - (row['yhat_upper'] - row['yhat']) / 2 * (current_k - k_up) / (k_down - k_up)

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values(1,{quantity}, 'BAL_UP_{row['code']}',0,{barrier},1,5,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)

    if row['current_k'] < k_down:
        current_k = max(row['current_k'], k_up)
        quantity = int(row['target_pos'] - row['pos'])
        barrier_bound = row['yhat_lower']
        barrier = row['yhat_lower'] + (row['yhat'] - row['yhat_lower']) / 2 * (k_down - current_k) / (k_down - k_up)

        query = f"""insert into public.orders_my(state, quantity, comment, remains, barrier, max_amount, pause, code,  order_type, barrier_bound)
                    values(1,{quantity}, 'BAL_DOWN_{row['code']}',0,{barrier},1,5,'{row['code']}', 'flt', {barrier_bound})
        """
        print(query)
        engine.execute(query)
