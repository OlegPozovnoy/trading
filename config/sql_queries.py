config = {
    "drop_view":  "DROP VIEW public.dealscandidates;",
    "create_view": """CREATE OR REPLACE VIEW public.dealscandidates
     AS
     SELECT l.index,
        l.min_start,
        l.max_start,
        l."end",
        l.sl,
        l.std,
        l.sec,
        l.price,
        l.mid,
        l.down,
        l.implied_prob,
        h.volume_inc,
        h.price_inc,
        h.lastprice,
        h.prct_inc,
        h.snaptimestamp,
        h.lastdealtime,
        q.ask,
        q.askamount,
        q.lot
       FROM ( SELECT bigdealshist.volume_inc,
                bigdealshist.price_inc,
                bigdealshist.lastprice,
                bigdealshist.prct_inc,
                bigdealshist.snaptimestamp,
                bigdealshist.code,
                bigdealshist.lastdealtime
               FROM bigdealshist) h
         JOIN (select * from df_levels where min_start is not null) l ON h.code::text = l.sec
         JOIN ( SELECT secquotes.code,
                secquotes.ask,
                secquotes.askamount,
                secquotes.lot
               FROM secquotes) q ON q.code::text = h.code::text
      WHERE h.price_inc > 0::double precision AND q.ask < l.max_start::double precision AND h.lastprice > l.min_start::double precision AND ((2::double precision * l."end"::double precision / (l.min_start::double precision + l.max_start::double precision) - 1::double precision) * 100::double precision) > 0.4::double precision
      ORDER BY h.snaptimestamp DESC;
    
    ALTER TABLE public.dealscandidates
        OWNER TO postgres;
    """
}


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