
monitor = {
    "non_filtered_query":  """select l.code, name as state, price, start, "end", std as new_std, now() as timestamp from df_all_levels l 
    inner join
    (
    select code, (bid + ask)/2 as price from public.futquotes where bid > 0
    union all
    select code, (bid + ask)/2 as price from public.secquotes where bid > 0) as q
    on l.code = q.code where 
    l.start <= q.price and l.end > q.price
    order by l.code desc""",

    "filtered_query": """select l.code, name as state, price, start, "end", std as new_std, now() as timestamp from df_all_levels l 
    inner join
    (
    select code, (bid + ask)/2 as price from public.futquotes where bid > 0
    union all
    select code, (bid + ask)/2 as price from public.secquotes where bid > 0) as q
    on l.code = q.code where 
    l.start <= q.price and l.end > q.price
	and l.code in (SELECT code from public.monitor_sec)
    order by l.code desc""",

}