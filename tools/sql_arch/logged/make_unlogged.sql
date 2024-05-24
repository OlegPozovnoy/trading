-- Table: public.secquotes
DROP VIEW public.allquotes_collat;
DROP VIEW public.pos_bollinger;
DROP VIEW public.quote_bollinger;
DROP VIEW public.vpnlext;
DROP VIEW public.vpnl;

DROP VIEW public.allquotes;
DROP VIEW public.allquotes_mini;
DROP VIEW public.report_futyield;
DROP VIEW public.potential;

DROP TABLE IF EXISTS public.futquotes;
DROP TABLE IF EXISTS public.secquotes;

CREATE  TABLE  IF NOT EXISTS public.secquotes
(
    fullid character varying(128) COLLATE pg_catalog."default" NOT NULL,
    instrumentid character varying(32) COLLATE pg_catalog."default",
    type character varying(16) COLLATE pg_catalog."default",
    code character varying(16) COLLATE pg_catalog."default",
    tradedate character varying(12) COLLATE pg_catalog."default",
    currency character varying(8) COLLATE pg_catalog."default",
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    lastprice double precision,
    volume double precision,
    prctchange double precision,
    lastdealtime character varying(32) COLLATE pg_catalog."default",
    session character varying(32) COLLATE pg_catalog."default",
    listing integer,
    valuedate character varying(16) COLLATE pg_catalog."default",
    isin character varying(16) COLLATE pg_catalog."default",
    lot integer,
    prec integer,
    pricestep double precision,
    lastdealqty bigint,
    lastdealvol double precision,
    updated_at timestamp with time zone,
    CONSTRAINT secquotes_pkey PRIMARY KEY (fullid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.secquotes
    OWNER to postgres;

-- Trigger: secquoteshisttrigger

-- DROP TRIGGER IF EXISTS secquoteshisttrigger ON public.secquotes;

CREATE OR REPLACE TRIGGER secquoteshisttrigger
    AFTER UPDATE
    ON public.secquotes
    FOR EACH ROW
    EXECUTE FUNCTION public.secquoteshistupd();

-- Trigger: updated_at_rule

-- DROP TRIGGER IF EXISTS updated_at_rule ON public.secquotes;

CREATE OR REPLACE TRIGGER updated_at_rule
    BEFORE INSERT OR UPDATE
    ON public.secquotes
    FOR EACH ROW
    EXECUTE FUNCTION public.updated_at_upd();

-- Table: public.futquotes

--

CREATE  TABLE IF NOT EXISTS public.futquotes
(
    fullid character varying(128) COLLATE pg_catalog."default" NOT NULL,
    code character varying(16) COLLATE pg_catalog."default",
    status character varying(16) COLLATE pg_catalog."default",
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    collateral double precision,
    minprice double precision,
    maxprice double precision,
    openinterest double precision,
    volume double precision,
    tillmaturity integer,
    maturitydate character varying(16) COLLATE pg_catalog."default",
    tradedate character varying(12) COLLATE pg_catalog."default",
    closeprice double precision,
    prctchange double precision,
    instrumentid character varying(32) COLLATE pg_catalog."default",
    lot integer,
    prec integer,
    pricestep double precision,
    lastdealqty bigint,
    lastdealvol double precision,
    pricestepcur double precision,
    updated_at timestamp with time zone,
    CONSTRAINT futquotes_pkey PRIMARY KEY (fullid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.futquotes
    OWNER to postgres;

-- Trigger: futquoteshisttrigger

-- DROP TRIGGER IF EXISTS futquoteshisttrigger ON public.futquotes;

CREATE OR REPLACE TRIGGER futquoteshisttrigger
    AFTER UPDATE
    ON public.futquotes
    FOR EACH ROW
    EXECUTE FUNCTION public.futquoteshistupd();

-- Trigger: updated_at_rule

-- DROP TRIGGER IF EXISTS updated_at_rule ON public.futquotes;

CREATE OR REPLACE TRIGGER updated_at_rule
    BEFORE INSERT OR UPDATE
    ON public.futquotes
    FOR EACH ROW
    EXECUTE FUNCTION public.updated_at_upd();
-- View: public.allquotes_collat

--

CREATE OR REPLACE VIEW public.allquotes_collat
 AS
 SELECT quotes.code,
    quotes.market,
    quotes.bid,
    quotes.bidamount,
    quotes.ask,
    quotes.askamount,
    quotes.mid,
    quotes.lot,
    quotes.dlong,
    quotes.dshort,
    money.money,
    money.money / (quotes.bid * quotes.lot::double precision * COALESCE(quotes.dlong, 1::double precision)) AS long_avail,
    money.money / (quotes.bid * quotes.lot::double precision * COALESCE(quotes.dshort, 1::double precision)) AS short_avail
   FROM ( SELECT futquotes.code,
            'SPBFUT'::text AS market,
            futquotes.bid,
            futquotes.bidamount,
            futquotes.ask,
            futquotes.askamount,
            (futquotes.bid + futquotes.ask) / 2::double precision AS mid,
            1 AS lot,
            futquotes.collateral / futquotes.ask AS dlong,
            futquotes.collateral / futquotes.ask AS dshort
           FROM futquotes
          WHERE futquotes.status::integer = 1 AND futquotes.bidamount > 0::double precision AND futquotes.askamount > 0::double precision
        UNION ALL
         SELECT secquotes.code,
            'TQBR'::text AS market,
            secquotes.bid,
            secquotes.bidamount,
            secquotes.ask,
            secquotes.askamount,
            (secquotes.bid + secquotes.ask) / 2::double precision AS mid,
            secquotes.lot,
            pos_collat.dlong,
            pos_collat.dshort
           FROM secquotes
             LEFT JOIN pos_collat ON secquotes.code::text = pos_collat.code::text
          WHERE secquotes.bidamount > 0::double precision AND secquotes.askamount > 0::double precision AND secquotes.session::integer = 1) quotes
     LEFT JOIN money ON quotes.market = money.board::text;

ALTER TABLE public.allquotes_collat
    OWNER TO postgres;

-- View: public.quote_bollinger

--

CREATE OR REPLACE VIEW public.quote_bollinger
 AS
 SELECT q.code,
    b.class_code,
    q.quote,
    (q.quote - b.mean) / b.std AS bollinger,
    b.count,
    b.up,
    b.down
   FROM ( SELECT futquotesdiff.code,
            (futquotesdiff.bid + futquotesdiff.ask) / 2::double precision AS quote
           FROM futquotesdiff
        UNION ALL
         SELECT secquotes.code,
            (secquotes.bid + secquotes.ask) / 2::double precision
           FROM secquotes) q
     JOIN df_bollinger b ON q.code::text = b.security
  WHERE q.quote > 0::double precision
  ORDER BY ((q.quote - b.mean) / b.std) DESC;

ALTER TABLE public.quote_bollinger
    OWNER TO postgres;

-- View: public.pos_bollinger

--

CREATE OR REPLACE VIEW public.pos_bollinger
 AS
 SELECT p.code,
    p.pos,
    p.buy,
    p.sell,
    p.pnl,
    p.price_balance,
    p.volume,
    p.firm,
    b.bollinger,
    b.count,
    b.up,
    b.down
   FROM quote_bollinger b
     JOIN united_pos p ON b.code::text = p.code::text;

ALTER TABLE public.pos_bollinger
    OWNER TO postgres;

-- View: public.vpnl

--

CREATE OR REPLACE VIEW public.vpnl
 AS
 SELECT d."time",
        CASE
            WHEN d.bs::text = 'BUY'::text THEN 1
            ELSE '-1'::integer
        END * d.amount AS amount,
    d.code,
    d.price AS in_price,
    q.price,
    d.volume,
    d.broker_fees,
        CASE
            WHEN d.bs::text = 'BUY'::text THEN 1
            ELSE '-1'::integer
        END::double precision * d.volume * (q.price / d.price - 1::double precision) - d.broker_fees AS pnl,
    q.lot
   FROM deals d
     JOIN ( SELECT futquotes.code,
            (futquotes.bid + futquotes.ask) / 2::double precision AS price,
            1 AS lot
           FROM futquotes
          WHERE futquotes.bid > 0::double precision
        UNION ALL
         SELECT secquotes.code,
            (secquotes.bid + secquotes.ask) / 2::double precision AS price,
            secquotes.lot
           FROM secquotes
          WHERE secquotes.bid > 0::double precision) q ON d.code::text = q.code::text;

ALTER TABLE public.vpnl
    OWNER TO postgres;


-- View: public.vpnlext

--

CREATE OR REPLACE VIEW public.vpnlext
 AS
 SELECT amount,
    code,
    mprice,
    pnl,
    amount::double precision * mprice * lot::double precision AS volume,
        CASE
            WHEN amount = 0::numeric THEN 0::double precision
            ELSE (mprice * lot::double precision - pnl) / amount::double precision
        END AS breakevenprice
   FROM ( SELECT sum(vpnl.amount) AS amount,
            vpnl.code,
            avg(vpnl.price) AS mprice,
            sum(vpnl.pnl) AS pnl,
            avg(vpnl.lot) AS lot
           FROM vpnl
          GROUP BY vpnl.code) l;

ALTER TABLE public.vpnlext
    OWNER TO postgres;

-- View: public.allquotes_mini

--

CREATE OR REPLACE VIEW public.allquotes_mini
 AS
 SELECT futquotes.code,
    'SPBFUT'::text AS market,
    futquotes.bid,
    futquotes.bidamount,
    futquotes.ask,
    futquotes.askamount,
    (futquotes.bid + futquotes.ask) / 2::double precision AS mid
   FROM futquotes
  WHERE futquotes.status::integer = 1 AND futquotes.bidamount > 0::double precision AND futquotes.askamount > 0::double precision
UNION ALL
 SELECT secquotes.code,
    'TQBR'::text AS market,
    secquotes.bid,
    secquotes.bidamount,
    secquotes.ask,
    secquotes.askamount,
    (secquotes.bid + secquotes.ask) / 2::double precision AS mid
   FROM secquotes
  WHERE secquotes.bidamount > 0::double precision AND secquotes.askamount > 0::double precision AND secquotes.session::integer = 1;

ALTER TABLE public.allquotes_mini
    OWNER TO postgres;

-- View: public.allquotes

--

CREATE OR REPLACE VIEW public.allquotes
 AS
 SELECT allquotes.code,
    allquotes.market,
    allquotes.bid,
    allquotes.bidamount,
    allquotes.ask,
    allquotes.askamount,
    allquotes.mid,
    ord.id,
    ord.activate_id,
    ord.state,
    ord.quantity,
    ord.comment,
    ord.remains,
    ord.stop_loss,
    ord.take_profit,
    ord.parent_id,
    ord.barrier,
    ord.max_amount,
    ord.pause,
    ord.direction,
    COALESCE(executed.amount::integer, 0) AS amount,
    COALESCE(executed.unconfirmed_amount::integer, 0) AS unconfirmed_amount,
    COALESCE(executed.amount_pending::integer, 0) AS amount_pending,
    ord.start_time,
    ord.end_time,
    ord.provider,
    minmax.min_5mins,
    minmax.max_5mins,
    ord.order_type,
    ord.barrier_bound
   FROM allquotes_mini allquotes
     LEFT JOIN ( SELECT orders_my.id,
            orders_my.activate_id,
            orders_my.state,
            orders_my.quantity,
            orders_my.comment,
            orders_my.remains,
            orders_my.stop_loss,
            orders_my.take_profit,
            orders_my.parent_id,
            orders_my.barrier,
            orders_my.max_amount,
            orders_my.pause,
            orders_my.code,
            orders_my.direction,
            orders_my.start_time,
            orders_my.end_time,
            orders_my.provider,
            orders_my.order_type,
            orders_my.barrier_bound
           FROM orders_my) ord ON allquotes.code::text = ord.code::text
     LEFT JOIN ( SELECT autoorders_grouped.code,
            autoorders_grouped.comment,
            autoorders_grouped.amount,
            autoorders_grouped.unconfirmed_amount,
            autoorders_grouped.amount_pending,
            NULL::text AS provider
           FROM autoorders_grouped
        UNION ALL
         SELECT autoorders_grouped_tcs.code,
            autoorders_grouped_tcs.comment,
            autoorders_grouped_tcs.amount,
            autoorders_grouped_tcs.unconfirmed_amount,
            autoorders_grouped_tcs.amount_pending,
            'tcs'::text AS provider
           FROM autoorders_grouped_tcs) executed ON executed.code = ord.code::text AND concat(ord.comment::text, ord.id) = executed.comment AND COALESCE(ord.provider, ''::character varying)::text = COALESCE(executed.provider, ''::text)
     LEFT JOIN ( SELECT diffminmax.code,
            diffminmax.min_5mins,
            diffminmax.max_5mins
           FROM diffminmax) minmax ON allquotes.code::text = minmax.code;

ALTER TABLE public.allquotes
    OWNER TO postgres;



-- View: public.report_futyield

--

CREATE OR REPLACE VIEW public.report_futyield
 AS
 SELECT fq.code AS futcode,
    (sq.bid + sq.ask) / 2::double precision AS secprice,
    (fq.bid + fq.ask) / 2::double precision / fq.lot::double precision AS futprice,
    fq.tillmaturity,
    100::double precision * (power((fq.bid + fq.ask) / fq.lot::double precision / (sq.bid + sq.ask), (365 / fq.tillmaturity)::double precision) - 1::double precision) AS yearly_prct,
    (100 * 365 / fq.tillmaturity)::double precision / power((fq.bid + fq.ask) / fq.lot::double precision / (sq.bid + sq.ask), (365 / fq.tillmaturity + 1)::double precision) / (fq.bid + fq.ask) * 2::double precision * fq.lot::double precision AS div_rub_adj,
    sq.code,
    fq.maturitydate,
    sq.lot,
    100::double precision * ((fq.bid + fq.ask) / fq.lot::double precision / (sq.bid + sq.ask) - 1::double precision) AS prct,
    fp.ticker,
    fp.futprefix
   FROM futquotes fq
     LEFT JOIN futprefix fp ON "left"(fq.code::text, 2) = fp.futprefix::text
     LEFT JOIN secquotes sq ON fp.ticker::text = sq.code::text
  ORDER BY fq.code;

ALTER TABLE public.report_futyield
    OWNER TO postgres;


-- View: public.potential

--

CREATE OR REPLACE VIEW public.potential
 AS
 SELECT (t2.max / t1.price - 1::double precision) * t1.leverage AS potential,
    t2.max,
    t1.price,
    t1.leverage,
    COALESCE(t1.code, t2.security) AS code,
    (t2.max / t1.price - 1::double precision) * t1.leverage / af.sigma AS potential_sharp,
    af.sigma
   FROM ( SELECT futquotes.code,
            (futquotes.bid + futquotes.ask) / 2::double precision AS price,
            (futquotes.bid + futquotes.ask) / 2::double precision / futquotes.collateral AS leverage
           FROM futquotes) t1
     FULL JOIN ( SELECT max(df_all_candles_t.close) AS max,
            df_all_candles_t.security
           FROM df_all_candles_t
          WHERE df_all_candles_t.class_code::text = 'SPBFUT'::text
          GROUP BY df_all_candles_t.security) t2 ON t1.code::text = t2.security::text
     LEFT JOIN analytics_future af ON af.sec = COALESCE(t1.code, t2.security)::text
  ORDER BY ((t2.max / t1.price - 1::double precision) * t1.leverage) DESC;

ALTER TABLE public.potential
    OWNER TO postgres;









