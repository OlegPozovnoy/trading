-- Table: public.orders_my
DROP VIEW public.jump_events;
DROP VIEW public.trd_mypos;
DROP VIEW public.allquotes;
DROP TABLE IF EXISTS public.orders_my;
DROP TABLE IF EXISTS public.diffhist_t1510;
DROP TABLE IF EXISTS public.orders_event_activator_jumps;
DROP TABLE IF EXISTS public.orders_event_activator_news;
DROP TABLE IF EXISTS public.orders_event_activator_price;

DROP SEQUENCE IF EXISTS public.orders_my_id_seq;

CREATE SEQUENCE IF NOT EXISTS public.orders_my_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;



CREATE UNLOGGED TABLE IF NOT EXISTS public.orders_my
(
    id integer NOT NULL DEFAULT nextval('orders_my_id_seq'::regclass),
    activate_id integer,
    state integer,
    quantity integer,
    comment character varying(128) COLLATE pg_catalog."default",
    remains integer,
    stop_loss double precision,
    take_profit double precision,
    parent_id integer,
    barrier double precision,
    max_amount integer,
    pause double precision,
    code character varying(32) COLLATE pg_catalog."default",
    direction integer,
    pending_conf integer,
    pending_unconf integer,
    end_time timestamp with time zone,
    start_time timestamp with time zone,
    provider character varying(8) COLLATE pg_catalog."default",
    order_type character varying(8) COLLATE pg_catalog."default",
    barrier_bound double precision,
    CONSTRAINT orders_my_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders_my
    OWNER to postgres;

ALTER SEQUENCE public.orders_my_id_seq
    OWNED BY public.orders_my.id;

ALTER SEQUENCE public.orders_my_id_seq
    OWNER TO postgres;
-- Table: public.diffhist_t1510

--

CREATE UNLOGGED TABLE IF NOT EXISTS public.diffhist_t1510
(
    index bigint,
    code text COLLATE pg_catalog."default",
    board text COLLATE pg_catalog."default",
    min double precision,
    max double precision,
    mean double precision,
    volume bigint,
    count bigint,
    min_datetime timestamp with time zone,
    max_datetime timestamp with time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.diffhist_t1510
    OWNER to postgres;
-- Index: ix_diffhist_index

-- DROP INDEX IF EXISTS public.ix_diffhist_index;

CREATE INDEX IF NOT EXISTS ix_diffhist_index
    ON public.diffhist_t1510 USING btree
    (index ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.orders_event_activator_jumps



CREATE UNLOGGED TABLE IF NOT EXISTS public.orders_event_activator_jumps
(
    id bigint NOT NULL DEFAULT nextval('orders_activator_shared_sequence'::regclass),
    ticker character varying(16) COLLATE pg_catalog."default" NOT NULL,
    start_date timestamp with time zone NOT NULL DEFAULT now(),
    end_date timestamp with time zone NOT NULL DEFAULT (now() + '00:00:01'::interval),
    is_activated boolean NOT NULL DEFAULT false,
    jump_prct double precision,
    out_prct double precision,
    volume_peak double precision,
    out_std double precision,
    activate_time timestamp with time zone,
    CONSTRAINT orders_event_activator_jumps_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders_event_activator_jumps
    OWNER to postgres;


-- Table: public.orders_event_activator_news

--

CREATE UNLOGGED TABLE IF NOT EXISTS public.orders_event_activator_news
(
    id bigint NOT NULL DEFAULT nextval('orders_activator_shared_sequence'::regclass),
    ticker character varying(16) COLLATE pg_catalog."default",
    keyword character varying(16) COLLATE pg_catalog."default",
    start_date timestamp with time zone DEFAULT now(),
    end_date timestamp with time zone DEFAULT (now() + '00:00:01'::interval),
    is_activated boolean DEFAULT false,
    activate_time timestamp with time zone,
    channel_source character varying(32) COLLATE pg_catalog."default" DEFAULT 'markettwits'::character varying,
    CONSTRAINT orders_event_activator_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders_event_activator_news
    OWNER to postgres;

-- Table: public.orders_event_activator_price

--

CREATE UNLOGGED TABLE IF NOT EXISTS public.orders_event_activator_price
(
    id bigint NOT NULL DEFAULT nextval('orders_activator_shared_sequence'::regclass),
    ticker character varying(16) COLLATE pg_catalog."default" NOT NULL,
    price_limit double precision,
    start_date timestamp with time zone NOT NULL DEFAULT now(),
    end_date timestamp with time zone NOT NULL DEFAULT (now() + '00:00:01'::interval),
    is_activated boolean NOT NULL DEFAULT false,
    activate_time timestamp with time zone,
    CONSTRAINT orders_event_activator_price_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.orders_event_activator_price
    OWNER to postgres;


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


-- View: public.jump_events

--

CREATE OR REPLACE VIEW public.jump_events
 AS
 SELECT dh.code,
    dh.min,
    dh.max,
    dh.mean,
    dh.volume,
    dh.count,
    fq.bid,
    fq.bidamount,
    fq.ask,
    fq.askamount,
    fq.volume_inc,
    fq.bid_inc,
    fq.ask_inc,
    fq.updated_at,
    fq.last_upd,
    fq.volume_wa,
    now() AS process_time,
    (fq.bid_inc + fq.ask_inc) / (fq.bid + fq.ask) * 100::double precision AS jump_prct,
        CASE
            WHEN fq.ask < dh.min THEN (- (dh.min / fq.ask - 1::double precision)) * 100::double precision
            ELSE (fq.bid / dh.max - 1::double precision) * 100::double precision
        END AS out_prct,
    round(fq.volume_inc * 10::double precision / dh.volume::double precision * dh.max) AS volume_peak,
        CASE
            WHEN fq.ask < dh.min THEN (fq.ask - dh.min) / (dh.max - dh.min)
            ELSE (fq.bid - dh.max) / (dh.max - dh.min)
        END AS out_std
   FROM diffhist_t1510 dh
     JOIN futquotesdiff fq ON dh.code = fq.code::text
  WHERE dh.volume > 0 AND (dh.max - dh.min) > 0::double precision AND (dh.volume::double precision * dh.max / 10::double precision) < fq.volume_inc AND (fq.ask < dh.min OR fq.bid > dh.max) AND fq.bid > 0::double precision;

ALTER TABLE public.jump_events
    OWNER TO postgres;





