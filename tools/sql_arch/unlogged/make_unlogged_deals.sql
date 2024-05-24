-- Table: public.deals
DROP VIEW public.vpnlext;
DROP VIEW public.vpnl;
DROP TABLE IF EXISTS public.deals;

CREATE UNLOGGED TABLE IF NOT EXISTS public.deals
(
    deal_id bigint NOT NULL,
    order_id bigint NOT NULL,
    "time" time without time zone,
    bs character varying(16) COLLATE pg_catalog."default",
    code character varying(32) COLLATE pg_catalog."default",
    price double precision,
    amount bigint,
    volume double precision,
    comment character varying(64) COLLATE pg_catalog."default",
    broker_fees double precision,
    tradedate date NOT NULL,
    class_code character varying(32) COLLATE pg_catalog."default",
    CONSTRAINT deals_pkey PRIMARY KEY (deal_id, tradedate)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.deals
    OWNER to postgres;


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

