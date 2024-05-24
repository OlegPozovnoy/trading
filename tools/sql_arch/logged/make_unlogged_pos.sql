-- Table: public.pos_collat
DROP VIEW public.trd_mypos;
DROP VIEW public.pos_bollinger;
DROP VIEW public.united_pos;
DROP VIEW public.allquotes_collat;
DROP VIEW public.money;
DROP TABLE IF EXISTS public.pos_collat;
DROP TABLE IF EXISTS public.pos_eq;
DROP TABLE IF EXISTS public.pos_fut;
DROP TABLE IF EXISTS public.pos_money;

CREATE  TABLE IF NOT EXISTS public.pos_collat
(
    instrument character varying(32) COLLATE pg_catalog."default",
    view character varying(8) COLLATE pg_catalog."default",
    type character varying(8) COLLATE pg_catalog."default",
    pos bigint,
    collateral double precision,
    account character varying(32) COLLATE pg_catalog."default",
    code character varying(16) COLLATE pg_catalog."default",
    volume double precision,
    dlong double precision,
    dshort double precision,
    CONSTRAINT pk_pos_collat UNIQUE (view, type, account, code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pos_collat
    OWNER to postgres;


-- Table: public.pos_eq

--

CREATE  TABLE IF NOT EXISTS public.pos_eq
(
    instrument character varying(32) COLLATE pg_catalog."default",
    pos bigint,
    price double precision,
    volume double precision,
    pnl double precision,
    buy bigint,
    sell bigint,
    tobuy bigint,
    tosell bigint,
    firm character varying(32) COLLATE pg_catalog."default",
    account character varying(32) COLLATE pg_catalog."default",
    client_id character varying(32) COLLATE pg_catalog."default",
    settlement character varying(4) COLLATE pg_catalog."default",
    code character varying(16) COLLATE pg_catalog."default",
    CONSTRAINT pk_pos_eq UNIQUE (firm, account, client_id, settlement, code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pos_eq
    OWNER to postgres;


-- Table: public.pos_fut

--

CREATE  TABLE IF NOT EXISTS public.pos_fut
(
    code character varying(16) COLLATE pg_catalog."default",
    instrument character varying(32) COLLATE pg_catalog."default",
    maturity date,
    pos bigint,
    buy bigint,
    sell bigint,
    pnl double precision,
    price_balance double precision,
    firm character varying(16) COLLATE pg_catalog."default",
    account character varying(16) COLLATE pg_catalog."default",
    type character varying(16) COLLATE pg_catalog."default",
    CONSTRAINT pk_pos_fut UNIQUE (code, firm, account, type)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pos_fut
    OWNER to postgres;



-- Table: public.pos_money

--

CREATE  TABLE IF NOT EXISTS public.pos_money
(
    money_prev double precision,
    money double precision,
    pos_current double precision,
    pos_plan double precision,
    pnl double precision,
    pnl_prev double precision,
    fees double precision,
    firm character varying(16) COLLATE pg_catalog."default",
    account character varying(16) COLLATE pg_catalog."default",
    type character varying(16) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pos_money
    OWNER to postgres;


-- View: public.money

--

CREATE OR REPLACE VIEW public.money
 AS
 SELECT pos_money.firm AS board,
    pos_money.pos_plan AS money
   FROM pos_money
UNION ALL
 SELECT 'TQBR'::character varying AS board,
    sum(pos_collat.volume) - sum(
        CASE
            WHEN pos_collat.code::text = 'SUR'::text THEN 0::double precision
            ELSE pos_collat.collateral
        END) AS money
   FROM pos_collat;

ALTER TABLE public.money
    OWNER TO postgres;



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


-- View: public.united_pos

--

CREATE OR REPLACE VIEW public.united_pos
 AS
 SELECT pos_fut.code,
    pos_fut.pos,
    pos_fut.buy,
    pos_fut.sell,
    pos_fut.pnl,
    pos_fut.price_balance,
    pos_fut.pos::double precision * pos_fut.price_balance * COALESCE(pos_volmult.multiplier, 1::double precision) + pos_fut.pnl AS volume,
    pos_fut.firm
   FROM pos_fut
     LEFT JOIN pos_volmult ON "left"(pos_fut.code::text, 2) = pos_volmult.code::text
  WHERE (abs(pos_fut.pos) + pos_fut.buy + pos_fut.sell) <> 0
UNION ALL
 SELECT pos_eq.code,
    pos_eq.pos,
    pos_eq.buy,
    pos_eq.sell,
    pos_eq.pnl,
    pos_eq.price AS price_balance,
    pos_eq.volume + pos_eq.pnl AS volume,
    'TQBR'::character varying AS firm
   FROM pos_eq
  WHERE (abs(pos_eq.pos) + pos_eq.buy + pos_eq.sell) <> 0;

ALTER TABLE public.united_pos
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





-- View: public.trd_mypos

--

CREATE OR REPLACE VIEW public.trd_mypos
 AS
 WITH pos_summary AS (
         SELECT united_pos.code,
            united_pos.pos,
            united_pos.pnl,
            united_pos.volume
           FROM united_pos
        UNION
         SELECT 'ZTOTAL'::character varying AS "varchar",
            0,
            sum(united_pos.pnl) AS sum,
            sum(united_pos.volume) AS sum
           FROM united_pos
        ), intervals AS (
         SELECT COALESCE(l_up.sec, l_down.sec) AS code,
            l_down.price AS down_price,
            COALESCE(l_up.price, 999999::double precision) AS up_price
           FROM df_levels l_up
             FULL JOIN df_levels l_down ON l_up.index = (l_down.index + 1) AND l_up.sec = l_down.sec
        ), orders AS (
         SELECT orders_my.code,
            count(*) AS ordnum,
            sum(orders_my.state) AS actnum
           FROM orders_my
          GROUP BY orders_my.code
        ), plita_bid AS (
         SELECT bids.code,
            bids.price AS bid,
            bids.quantity AS bid_qty
           FROM report_plita bids
          WHERE bids.ba = 'bid'::text
        ), plita_ask AS (
         SELECT asks.code,
            asks.price AS ask,
            asks.quantity AS ask_qty
           FROM report_plita asks
          WHERE asks.ba = 'ask'::text
        )
 SELECT pos.code,
    pos.pos,
    pos.pnl,
    df_monitor.new_price AS mktprice,
    pos.volume,
    round(intervals.down_price::numeric, 4) AS lower,
    round(intervals.up_price::numeric, 4) AS upper,
    round((df_monitor.new_price - intervals.down_price)::numeric / (intervals.up_price - intervals.down_price)::numeric, 2) AS levels,
    df_monitor.new_state,
    COALESCE(orders.ordnum, 0::bigint) AS ordnum,
    COALESCE(orders.actnum, 0::bigint) AS actnum,
    plita_bid.bid,
    plita_bid.bid_qty,
    plita_ask.ask,
    plita_ask.ask_qty
   FROM pos_summary pos
     LEFT JOIN df_monitor df_monitor ON df_monitor.code = pos.code::text
     LEFT JOIN intervals ON pos.code::text = intervals.code AND df_monitor.new_price >= intervals.down_price AND df_monitor.new_price < intervals.up_price
     LEFT JOIN orders ON pos.code::text = orders.code::text
     LEFT JOIN plita_bid ON pos.code::text = plita_bid.code
     LEFT JOIN plita_ask ON pos.code::text = plita_ask.code
  ORDER BY pos.code;

ALTER TABLE public.trd_mypos
    OWNER TO postgres;






