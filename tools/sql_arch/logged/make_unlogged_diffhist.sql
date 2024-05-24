-- Table: public.secquotesdiff
DROP VIEW public.deals_ba_view;
DROP VIEW public.pos_bollinger;
DROP VIEW public.quote_bollinger;
DROP VIEW public.allquotes;
DROP VIEW public.diffminmax;
DROP VIEW public.jump_events;
DROP TABLE IF EXISTS public.secquotesdiff;
DROP TABLE IF EXISTS public.futquotesdiff;
DROP TABLE IF EXISTS public.func_stats;
DROP TABLE IF EXISTS public.deals_ba;

CREATE  TABLE IF NOT EXISTS public.secquotesdiff
(
    code character varying(16) COLLATE pg_catalog."default" NOT NULL,
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    volume double precision,
    volume_inc double precision,
    bid_inc double precision,
    ask_inc double precision,
    updated_at timestamp with time zone,
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision,
    CONSTRAINT secquotesdiff_pkey PRIMARY KEY (code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.secquotesdiff
    OWNER to postgres;

-- Trigger: last_upd_rule

-- DROP TRIGGER IF EXISTS last_upd_rule ON public.secquotesdiff;

CREATE OR REPLACE TRIGGER last_upd_rule
    BEFORE INSERT OR UPDATE
    ON public.secquotesdiff
    FOR EACH ROW
    EXECUTE FUNCTION public.last_upd_upd();

-- Trigger: secquotesdiffhist_upd

-- DROP TRIGGER IF EXISTS secquotesdiffhist_upd ON public.secquotesdiff;

CREATE OR REPLACE TRIGGER secquotesdiffhist_upd
    AFTER INSERT OR UPDATE
    ON public.secquotesdiff
    FOR EACH ROW
    EXECUTE FUNCTION public.secquotesdiffhistupd();


-- Table: public.futquotesdiff

--

CREATE  TABLE IF NOT EXISTS public.futquotesdiff
(
    code character varying(16) COLLATE pg_catalog."default" NOT NULL,
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    openinterest double precision,
    volume double precision,
    volume_inc double precision,
    bid_inc double precision,
    ask_inc double precision,
    updated_at timestamp with time zone,
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision,
    CONSTRAINT futquotesdiff_pkey PRIMARY KEY (code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.futquotesdiff
    OWNER to postgres;

-- Trigger: futquotesdiffhist_upd

-- DROP TRIGGER IF EXISTS futquotesdiffhist_upd ON public.futquotesdiff;

CREATE OR REPLACE TRIGGER futquotesdiffhist_upd
    AFTER INSERT OR UPDATE
    ON public.futquotesdiff
    FOR EACH ROW
    EXECUTE FUNCTION public.futquotesdiffhistupd();

-- Trigger: last_upd_rule

-- DROP TRIGGER IF EXISTS last_upd_rule ON public.futquotesdiff;

CREATE OR REPLACE TRIGGER last_upd_rule
    BEFORE INSERT OR UPDATE
    ON public.futquotesdiff
    FOR EACH ROW
    EXECUTE FUNCTION public.last_upd_upd();

-- Table: public.func_stats

--

CREATE  TABLE IF NOT EXISTS public.func_stats
(
    name character varying(64) COLLATE pg_catalog."default" NOT NULL,
    num bigint,
    avg double precision,
    min double precision,
    max double precision,
    stdev double precision,
    last double precision,
    last_invoke timestamp with time zone DEFAULT now(),
    CONSTRAINT func_stats_pkey PRIMARY KEY (name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.func_stats
    OWNER to postgres;


-- Table: public.deals_ba



CREATE  TABLE IF NOT EXISTS public.deals_ba
(
    code character varying(16) COLLATE pg_catalog."default" NOT NULL,
    bid bigint,
    price double precision NOT NULL,
    ask bigint,
    updated_at timestamp with time zone,
    CONSTRAINT deals_ba_pkey PRIMARY KEY (code, price)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.deals_ba
    OWNER to postgres;

-- Trigger: updated_at_rule

-- DROP TRIGGER IF EXISTS updated_at_rule ON public.deals_ba;

CREATE OR REPLACE TRIGGER updated_at_rule
    BEFORE INSERT OR UPDATE
    ON public.deals_ba
    FOR EACH ROW
    EXECUTE FUNCTION public.updated_at_upd();

-- View: public.diffminmax

--

CREATE OR REPLACE VIEW public.diffminmax
 AS
 SELECT code,
    board,
    min(min) AS min_5mins,
    max(max) AS max_5mins
   FROM ( SELECT diffhist_t5.code,
            diffhist_t5.board,
            diffhist_t5.min,
            diffhist_t5.max
           FROM diffhist_t5
        UNION ALL
         SELECT futquotesdiff.code,
            'SPBFUT'::text AS text,
            futquotesdiff.min_5mins,
            futquotesdiff.max_5mins
           FROM futquotesdiff
        UNION ALL
         SELECT secquotesdiff.code,
            'TQBR'::text AS text,
            secquotesdiff.min_5mins,
            secquotesdiff.max_5mins
           FROM secquotesdiff) t
  WHERE min IS NOT NULL AND max IS NOT NULL
  GROUP BY code, board;

ALTER TABLE public.diffminmax
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


-- View: public.deals_ba_view

--

CREATE OR REPLACE VIEW public.deals_ba_view
 AS
 SELECT COALESCE(deals_ba.code, deals_ba_t1.code) AS code,
    COALESCE(deals_ba.price, deals_ba_t1.price) AS price,
    now() AS last_upd,
    deals_ba.bid,
    deals_ba.ask,
    deals_ba.updated_at,
    deals_ba_t1.bid AS bidt1,
    deals_ba_t1.ask AS askt1,
    deals_ba_t1.updated_at AS updated_at_t1,
    deals_ba.bid - deals_ba_t1.bid AS dbid,
    deals_ba.ask - deals_ba_t1.ask AS dask
   FROM deals_ba
     FULL JOIN deals_ba_t1 ON deals_ba.price = deals_ba_t1.price AND deals_ba.code::text = deals_ba_t1.code::text;

ALTER TABLE public.deals_ba_view
    OWNER TO postgres;



