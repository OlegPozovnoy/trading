--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.3 (Ubuntu 15.3-1.pgdg22.04+1)

-- Started on 2023-06-10 04:38:30 MSK

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 282 (class 1255 OID 24577)
-- Name: bigdealhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.bigdealhistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
    IF NEW.volume - OLD.volume > 1000000 THEN
        INSERT INTO public.bigdealshist ( 
            volume_inc, 
            price_inc, 
            prct_inc, 
            fullid, 
            instrumentid, 
            type, 
            code, 
            currency, 
            bid, 
            bidamount, 
            ask, 
            askamount, 
            lastprice, 
            volume, 
            prctchange, 
            lastdealtime, 
            listing, 
            isin, 
			tradedate, 
			updated_at)

        VALUES(
            (NEW.volume - OLD.volume)/1000000, 
            NEW.lastprice - OLD.lastprice,
            NEW.prctchange - OLD.prctchange, 
            NEW.fullid, 
            NEW.instrumentid, 
            NEW.type, 
            NEW.code, 
            NEW.currency, 
            NEW.bid, 
            NEW.bidamount, 
            NEW.ask, 
            NEW.askamount, 
            NEW.lastprice, 
            NEW.volume, 
            NEW.prctchange, 
            NEW.lastdealtime, 
            NEW.listing, 
            NEW.isin,
			NEW.tradedate,
			NEW.updated_at
		);
    END IF;
    RETURN NEW;
END;

$$;


ALTER FUNCTION public.bigdealhistupd() OWNER TO postgres;

--
-- TOC entry 270 (class 1255 OID 109095)
-- Name: futquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.futquotesdiffhistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO futquotesdiffhist(code, bid, bidamount, ask, askamount, openinterest, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.openinterest, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.futquotesdiffhistupd() OWNER TO postgres;

--
-- TOC entry 283 (class 1255 OID 24578)
-- Name: futquoteshistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.futquoteshistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO futquoteshist(fullid, code, status, bid, bidamount, ask, askamount, collateral, minprice, maxprice, openinterest, volume, tillmaturity, maturitydate, tradedate, closeprice, prctchange, instrumentid, lot, prec, pricestep, lastdealqty, lastdealvol, pricestepcur, updated_at)

         VALUES(NEW.fullid, NEW.code, NEW.status, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, 
				NEW.collateral, NEW.minprice, NEW.maxprice, NEW.openinterest, NEW.volume, 
				NEW.tillmaturity, NEW.maturitydate, NEW.tradedate, NEW.closeprice, NEW.prctchange, 
				NEW.instrumentid, NEW.lot, NEW.prec, NEW.pricestep, NEW.lastdealqty, NEW.lastdealvol, 
				NEW.pricestepcur, NEW.updated_at);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.futquoteshistupd() OWNER TO postgres;

--
-- TOC entry 268 (class 1255 OID 109041)
-- Name: last_upd_upd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.last_upd_upd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_upd = now();
    RETURN NEW;   
END;
$$;


ALTER FUNCTION public.last_upd_upd() OWNER TO postgres;

--
-- TOC entry 269 (class 1255 OID 139041)
-- Name: secquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.secquotesdiffhistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO secquotesdiffhist(code, bid, bidamount, ask, askamount, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.secquotesdiffhistupd() OWNER TO postgres;

--
-- TOC entry 267 (class 1255 OID 24580)
-- Name: secquoteshistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.secquoteshistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO secquoteshist ( fullid, instrumentid, type, code, tradedate, currency, bid, bidamount, ask, askamount, lastprice, volume, prctchange, lastdealtime, session, listing, valuedate, isin, updated_at, lot, prec, pricestep, lastdealqty, lastdealvol)

         VALUES(NEW.fullid, NEW.instrumentid, NEW.type, NEW.code, NEW.tradedate, NEW.currency, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.lastprice, NEW.volume, NEW.prctchange, NEW.lastdealtime, NEW.session, NEW.listing, NEW.valuedate, NEW.isin, NEW.updated_at, NEW.lot, NEW.prec, NEW.pricestep, NEW.lastdealqty, NEW.lastdealvol);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.secquoteshistupd() OWNER TO postgres;

--
-- TOC entry 266 (class 1255 OID 108787)
-- Name: updated_at_upd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.updated_at_upd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
    NEW.updated_at = now();
    RETURN NEW;   
END;
$$;


ALTER FUNCTION public.updated_at_upd() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 36203)
-- Name: deorders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deorders (
    order_id bigint,
    tradedate date,
    dateopen date,
    timeopen time without time zone,
    datecancel date,
    timecancel time without time zone,
    code character varying(32),
    instrument character varying(32),
    bs character varying(16),
    price double precision,
    orderamount bigint,
    orderremains bigint,
    orderexecuted bigint,
    volume double precision,
    comment character varying(32),
    type character varying(16),
    state character varying(16),
    volumecalc double precision,
    class_code character varying(16),
    cancelreason text,
    execmode character varying(16),
    mcsopen bigint,
    mcscancel bigint,
    trans_id bigint
);


ALTER TABLE public.deorders OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 114124)
-- Name: orders_in; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_in (
    index bigint,
    "TRANS_ID" text,
    "CLIENT_CODE" text,
    "ACCOUNT" text,
    "ACTION" text,
    "CLASSCODE" text,
    "SECCODE" text,
    "OPERATION" text,
    "PRICE" text,
    "QUANTITY" text,
    "COMMENT" text,
    "TYPE" text,
    last_upd timestamp with time zone
);


ALTER TABLE public.orders_in OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 114130)
-- Name: orders_out; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_out (
    index bigint,
    firm_id text,
    order_flags bigint,
    date_time timestamp without time zone,
    sent_local_time timestamp without time zone,
    flags bigint,
    price double precision,
    "time" bigint,
    sec_code text,
    trans_id bigint,
    status bigint,
    exchange_code text,
    result_msg text,
    first_ordernum bigint,
    quantity double precision,
    uid bigint,
    brokerref text,
    account text,
    client_code text,
    balance double precision,
    got_local_time timestamp without time zone,
    order_num bigint,
    gate_reply_time timestamp without time zone,
    server_trans_id bigint,
    error_source bigint,
    error_code bigint,
    class_code text
);


ALTER TABLE public.orders_out OWNER TO postgres;

--
-- TOC entry 261 (class 1259 OID 297645)
-- Name: autoorders; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.autoorders AS
 SELECT oin."TRANS_ID",
    COALESCE(max_confirmed_id.last_confirmed_id, (0)::bigint) AS last_confirmed_id,
        CASE
            WHEN ((COALESCE(max_confirmed_id.last_confirmed_id, (0)::bigint) < (oin."TRANS_ID")::bigint) AND (oout.status IS NULL)) THEN (oin."QUANTITY")::bigint
            ELSE (0)::bigint
        END AS unconfirmed_quantity,
    oin."ACCOUNT",
    oin."ACTION",
    oin."CLASSCODE",
    oin."SECCODE",
    oin."OPERATION",
    oin."PRICE",
    oin."COMMENT",
    oin."QUANTITY",
    oin.last_upd AS in_last_upd,
    oout.date_time,
    oout.sent_local_time,
    oout."time",
    oout.trans_id,
    oout.status,
    oout.result_msg,
    oout.quantity,
    oout.got_local_time,
    oout.order_num,
    oout.gate_reply_time,
    oout.error_source,
    oout.error_code,
    dord.trans_id AS ord_trans_id,
    dord.order_id,
    dord.tradedate,
    dord.dateopen,
    dord.timeopen,
    dord.datecancel,
    dord.timecancel,
    dord.orderremains,
    dord.orderexecuted,
    dord.volume,
    dord.state,
    dord.volumecalc,
    dord.cancelreason,
    dord.execmode
   FROM (((( SELECT orders_in."TRANS_ID",
            orders_in."ACCOUNT",
            orders_in."ACTION",
            orders_in."CLASSCODE",
            orders_in."SECCODE",
            orders_in."OPERATION",
            orders_in."PRICE",
            orders_in."COMMENT",
            orders_in."QUANTITY",
            orders_in.last_upd
           FROM public.orders_in) oin
     LEFT JOIN ( SELECT orders_out.date_time,
            orders_out.sent_local_time,
            orders_out."time",
            orders_out.trans_id,
            orders_out.status,
            orders_out.result_msg,
            orders_out.quantity,
            orders_out.got_local_time,
            orders_out.order_num,
            orders_out.gate_reply_time,
            orders_out.error_source,
            orders_out.error_code
           FROM public.orders_out) oout ON (((oin."TRANS_ID")::bigint = oout.trans_id)))
     LEFT JOIN ( SELECT deorders.order_id,
            deorders.trans_id,
            deorders.tradedate,
            deorders.dateopen,
            deorders.timeopen,
            deorders.datecancel,
            deorders.timecancel,
            deorders.orderremains,
            deorders.orderexecuted,
            deorders.volume,
            deorders.state,
            deorders.volumecalc,
            deorders.cancelreason,
            deorders.execmode
           FROM public.deorders) dord ON (((oin."TRANS_ID")::bigint = dord.trans_id)))
     LEFT JOIN ( SELECT deorders.code,
            max(COALESCE(deorders.trans_id, (0)::bigint)) AS last_confirmed_id
           FROM public.deorders
          GROUP BY deorders.code) max_confirmed_id ON ((oin."SECCODE" = (max_confirmed_id.code)::text)));


ALTER TABLE public.autoorders OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 24633)
-- Name: futquotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.futquotes (
    fullid character varying(128),
    code character varying(16),
    status character varying(16),
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
    maturitydate character varying(16),
    tradedate character varying(12),
    closeprice double precision,
    prctchange double precision,
    instrumentid character varying(32),
    lot integer,
    prec integer,
    pricestep double precision,
    lastdealqty bigint,
    lastdealvol double precision,
    pricestepcur double precision,
    updated_at timestamp with time zone
);


ALTER TABLE public.futquotes OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24645)
-- Name: orders_my; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_my (
    id integer NOT NULL,
    activate double precision,
    activate_sign integer,
    deactivate double precision,
    deactivate_sign integer,
    state integer,
    quantity integer,
    comment character varying(128),
    remains integer,
    stop_loss double precision,
    take_profit double precision,
    parent_id integer,
    barrier double precision,
    max_amount integer,
    pause double precision,
    code character varying(32),
    direction integer,
    pending_conf integer,
    pending_unconf integer,
    end_time timestamp with time zone,
    start_time timestamp with time zone
);


ALTER TABLE public.orders_my OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 24593)
-- Name: secquotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secquotes (
    fullid character varying(128),
    instrumentid character varying(32),
    type character varying(16),
    code character varying(16),
    tradedate character varying(12),
    currency character varying(8),
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    lastprice double precision,
    volume double precision,
    prctchange double precision,
    lastdealtime character varying(32),
    session character varying(32),
    listing integer,
    valuedate character varying(16),
    isin character varying(16),
    lot integer,
    prec integer,
    pricestep double precision,
    lastdealqty bigint,
    lastdealvol double precision,
    updated_at timestamp with time zone
);


ALTER TABLE public.secquotes OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 297650)
-- Name: allquotes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.allquotes AS
 SELECT allquotes.code,
    allquotes.market,
    allquotes.bid,
    allquotes.bidamount,
    allquotes.ask,
    allquotes.askamount,
    allquotes.mid,
    ord.id,
    ord.activate,
    ord.activate_sign,
    ord.deactivate,
    ord.deactivate_sign,
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
    COALESCE((executed.amount)::integer, 0) AS amount,
    COALESCE((executed.unconfirmed_amount)::integer, 0) AS unconfirmed_amount,
    COALESCE((executed.amount_pending)::integer, 0) AS amount_pending
   FROM ((( SELECT futquotes.code,
            'SPBFUT'::text AS market,
            futquotes.bid,
            futquotes.bidamount,
            futquotes.ask,
            futquotes.askamount,
            ((futquotes.bid + futquotes.ask) / (2)::double precision) AS mid
           FROM public.futquotes
          WHERE (((futquotes.status)::integer = 1) AND (futquotes.bidamount > (0)::double precision) AND (futquotes.askamount > (0)::double precision))
        UNION ALL
         SELECT secquotes.code,
            'TQBR'::text AS market,
            secquotes.bid,
            secquotes.bidamount,
            secquotes.ask,
            secquotes.askamount,
            ((secquotes.bid + secquotes.ask) / (2)::double precision) AS mid
           FROM public.secquotes
          WHERE ((secquotes.bidamount > (0)::double precision) AND (secquotes.askamount > (0)::double precision) AND ((secquotes.session)::integer = 1))) allquotes
     LEFT JOIN ( SELECT orders_my.id,
            orders_my.activate,
            orders_my.activate_sign,
            orders_my.deactivate,
            orders_my.deactivate_sign,
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
            orders_my.direction
           FROM public.orders_my) ord ON (((allquotes.code)::text = (ord.code)::text)))
     LEFT JOIN ( SELECT autoorders."SECCODE" AS code,
            autoorders."COMMENT" AS comment,
            sum((COALESCE((autoorders.orderexecuted)::integer, 0) *
                CASE
                    WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
                    WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
                    ELSE 0
                END)) AS amount,
            sum((COALESCE((autoorders.unconfirmed_quantity)::integer, 0) *
                CASE
                    WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
                    WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
                    ELSE 0
                END)) AS unconfirmed_amount,
            sum(((COALESCE((autoorders.orderremains)::integer, 0) *
                CASE
                    WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
                    WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
                    ELSE 0
                END) *
                CASE
                    WHEN ((autoorders.state)::text = 'ACTIVE'::text) THEN 1
                    ELSE 0
                END)) AS amount_pending
           FROM public.autoorders
          GROUP BY autoorders."SECCODE", autoorders."COMMENT") executed ON (((executed.code = (ord.code)::text) AND (concat((ord.comment)::text, ord.id) = executed.comment))));


ALTER TABLE public.allquotes OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 263064)
-- Name: pos_collat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pos_collat (
    instrument character varying(32),
    view character varying(8),
    type character varying(8),
    pos bigint,
    collateral double precision,
    account character varying(32),
    code character varying(16),
    volume double precision,
    dlong double precision,
    dshort double precision
);


ALTER TABLE public.pos_collat OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 36707)
-- Name: pos_money; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pos_money (
    money_prev double precision,
    money double precision,
    pos_current double precision,
    pos_plan double precision,
    pnl double precision,
    pnl_prev double precision,
    fees double precision,
    firm character varying(16),
    account character varying(16),
    type character varying(16)
);


ALTER TABLE public.pos_money OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 263067)
-- Name: money; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.money AS
 SELECT pos_money.firm AS board,
    pos_money.pos_plan AS money
   FROM public.pos_money
UNION ALL
 SELECT 'TQBR'::character varying AS board,
    (sum(pos_collat.volume) - sum(
        CASE
            WHEN ((pos_collat.code)::text = 'SUR'::text) THEN (0)::double precision
            ELSE pos_collat.collateral
        END)) AS money
   FROM public.pos_collat;


ALTER TABLE public.money OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 322202)
-- Name: allquotes_collat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.allquotes_collat AS
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
    (money.money / ((quotes.bid * (quotes.lot)::double precision) * COALESCE(quotes.dlong, (1)::double precision))) AS long_avail,
    (money.money / ((quotes.bid * (quotes.lot)::double precision) * COALESCE(quotes.dshort, (1)::double precision))) AS short_avail
   FROM (( SELECT futquotes.code,
            'SPBFUT'::text AS market,
            futquotes.bid,
            futquotes.bidamount,
            futquotes.ask,
            futquotes.askamount,
            ((futquotes.bid + futquotes.ask) / (2)::double precision) AS mid,
            1 AS lot,
            (futquotes.collateral / futquotes.ask) AS dlong,
            (futquotes.collateral / futquotes.ask) AS dshort
           FROM public.futquotes
          WHERE (((futquotes.status)::integer = 1) AND (futquotes.bidamount > (0)::double precision) AND (futquotes.askamount > (0)::double precision))
        UNION ALL
         SELECT secquotes.code,
            'TQBR'::text AS market,
            secquotes.bid,
            secquotes.bidamount,
            secquotes.ask,
            secquotes.askamount,
            ((secquotes.bid + secquotes.ask) / (2)::double precision) AS mid,
            secquotes.lot,
            pos_collat.dlong,
            pos_collat.dshort
           FROM (public.secquotes
             LEFT JOIN public.pos_collat ON (((secquotes.code)::text = (pos_collat.code)::text)))
          WHERE ((secquotes.bidamount > (0)::double precision) AND (secquotes.askamount > (0)::double precision) AND ((secquotes.session)::integer = 1))) quotes
     LEFT JOIN public.money ON ((quotes.market = (money.board)::text)));


ALTER TABLE public.allquotes_collat OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 322190)
-- Name: autoorders_grouped; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.autoorders_grouped AS
 SELECT autoorders."SECCODE" AS code,
    autoorders."COMMENT" AS comment,
    sum((COALESCE((autoorders.orderexecuted)::integer, 0) *
        CASE
            WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
            WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
            ELSE 0
        END)) AS amount,
    sum((COALESCE((autoorders.unconfirmed_quantity)::integer, 0) *
        CASE
            WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
            WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
            ELSE 0
        END)) AS unconfirmed_amount,
    sum(((COALESCE((autoorders.orderremains)::integer, 0) *
        CASE
            WHEN (autoorders."OPERATION" = 'S'::text) THEN '-1'::integer
            WHEN (autoorders."OPERATION" = 'B'::text) THEN 1
            ELSE 0
        END) *
        CASE
            WHEN ((autoorders.state)::text = 'ACTIVE'::text) THEN 1
            ELSE 0
        END)) AS amount_pending
   FROM public.autoorders
  GROUP BY autoorders."SECCODE", autoorders."COMMENT";


ALTER TABLE public.autoorders_grouped OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 24581)
-- Name: bigdealshist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bigdealshist (
    volume_inc double precision,
    price_inc double precision,
    prct_inc double precision,
    snaptimestamp time with time zone DEFAULT now(),
    fullid character varying(128),
    instrumentid character varying(32),
    type character varying(16),
    code character varying(16),
    currency character varying(8),
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    lastprice double precision,
    volume double precision,
    prctchange double precision,
    lastdealtime character varying(32),
    listing integer,
    isin character varying(16),
    tradedate character varying(16),
    updated_at timestamp with time zone
);


ALTER TABLE public.bigdealshist OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 24585)
-- Name: deals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deals (
    deal_id bigint,
    order_id bigint,
    "time" time without time zone,
    bs character varying(16),
    code character varying(32),
    price double precision,
    amount bigint,
    volume double precision,
    comment character varying(64),
    broker_fees double precision,
    tradedate date,
    class_code character varying(32)
);


ALTER TABLE public.deals OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 122316)
-- Name: deals_all; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deals_all (
    "time" time without time zone,
    bs character varying(16),
    tr_period character varying(16),
    code character varying(32),
    price double precision,
    open_interest double precision,
    mcs double precision,
    amount bigint,
    tradedate date,
    class_code character varying(32)
);


ALTER TABLE public.deals_all OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 139070)
-- Name: df_all_candles_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_all_candles_t (
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    close double precision NOT NULL,
    volume integer NOT NULL,
    security character varying(64) NOT NULL,
    class_code character varying(64),
    datetime timestamp with time zone NOT NULL
);


ALTER TABLE public.df_all_candles_t OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 139031)
-- Name: df_all_candles_t_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_all_candles_t_arch (
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    close double precision NOT NULL,
    volume integer NOT NULL,
    security character varying(64) NOT NULL,
    class_code character varying(64),
    datetime timestamp with time zone NOT NULL
);


ALTER TABLE public.df_all_candles_t_arch OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 112446)
-- Name: df_all_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_all_levels (
    index bigint,
    code text,
    name text,
    start double precision,
    "end" double precision,
    logic bigint,
    std double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.df_all_levels OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 112457)
-- Name: df_all_volumes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_all_volumes (
    index bigint,
    price double precision,
    volume double precision,
    code text
);


ALTER TABLE public.df_all_volumes OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 97820)
-- Name: df_bollinger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_bollinger (
    index bigint,
    security text,
    class_code text,
    mean double precision,
    std double precision,
    count bigint,
    prct double precision,
    up double precision,
    down double precision
);


ALTER TABLE public.df_bollinger OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 130585)
-- Name: df_jumps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_jumps (
    level_0 bigint,
    code text,
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
    index bigint,
    security text,
    max_volume bigint,
    spread double precision,
    dt timestamp without time zone,
    cnt bigint,
    now timestamp with time zone
);


ALTER TABLE public.df_jumps OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 112440)
-- Name: df_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_levels (
    index bigint,
    price double precision,
    volume double precision,
    std double precision,
    sec text,
    min_start double precision,
    max_start double precision,
    "end" double precision,
    sl double precision,
    mid double precision,
    down text,
    prev_end double precision,
    next_sl double precision,
    implied_prob double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.df_levels OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 113090)
-- Name: df_monitor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_monitor (
    index bigint,
    code text,
    old_state text,
    old_price double precision,
    old_start double precision,
    old_end double precision,
    new_state text,
    new_price double precision,
    new_start double precision,
    new_end double precision,
    std double precision,
    old_timestamp timestamp with time zone,
    new_timestamp timestamp with time zone
);


ALTER TABLE public.df_monitor OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 130562)
-- Name: df_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_stats (
    index bigint,
    security text,
    max_volume integer,
    spread double precision,
    dt timestamp without time zone,
    cnt bigint
);


ALTER TABLE public.df_stats OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 97826)
-- Name: df_volumes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.df_volumes (
    index bigint,
    security text,
    class_code text,
    "time" time without time zone,
    mean double precision,
    std double precision,
    count bigint,
    close double precision,
    prct double precision,
    up double precision,
    mean_avg double precision,
    std_avg double precision,
    up_avga double precision,
    close_avg double precision
);


ALTER TABLE public.df_volumes OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 109061)
-- Name: futquotesdiffhist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.futquotesdiffhist (
    code character varying(16),
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
    last_upd timestamp with time zone
);


ALTER TABLE public.futquotesdiffhist OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 139037)
-- Name: secquotesdiffhist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secquotesdiffhist (
    code character varying(16),
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    volume double precision,
    volume_inc double precision,
    bid_inc double precision,
    ask_inc double precision,
    updated_at timestamp with time zone,
    last_upd timestamp with time zone
);


ALTER TABLE public.secquotesdiffhist OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 230274)
-- Name: diffhistview; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview AS
 SELECT secquotesdiffhist.code,
    'TQBR'::text AS board,
    min(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS min,
    max(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS max,
    sum(secquotesdiffhist.volume_inc) AS volume,
    count(*) AS count
   FROM public.secquotesdiffhist
  WHERE (secquotesdiffhist.last_upd > (now() - '00:01:00'::interval))
  GROUP BY secquotesdiffhist.code
 HAVING (min(secquotesdiffhist.bid) > (0)::double precision)
UNION ALL
 SELECT futquotesdiffhist.code,
    'SPBFUT'::text AS board,
    min(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS min,
    max(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS max,
    sum(futquotesdiffhist.volume_inc) AS volume,
    count(*) AS count
   FROM public.futquotesdiffhist
  WHERE (futquotesdiffhist.last_upd > (now() - '00:01:00'::interval))
  GROUP BY futquotesdiffhist.code
 HAVING (min(futquotesdiffhist.bid) > (0)::double precision);


ALTER TABLE public.diffhistview OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 263052)
-- Name: diffhistview_1510; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview_1510 AS
 SELECT secquotesdiffhist.code,
    'TQBR'::text AS board,
    min(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS min,
    max(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS max,
    avg(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS mean,
    sum(secquotesdiffhist.volume_inc) AS volume,
    count(*) AS count
   FROM public.secquotesdiffhist
  WHERE (((now() - '00:05:00'::interval) > secquotesdiffhist.last_upd) AND (secquotesdiffhist.last_upd > (now() - '00:15:00'::interval)))
  GROUP BY secquotesdiffhist.code
 HAVING (min(secquotesdiffhist.bid) > (0)::double precision)
UNION ALL
 SELECT futquotesdiffhist.code,
    'SPBFUT'::text AS board,
    min(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS min,
    max(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS max,
    avg(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS mean,
    sum(futquotesdiffhist.volume_inc) AS volume,
    count(*) AS count
   FROM public.futquotesdiffhist
  WHERE (((now() - '00:05:00'::interval) > futquotesdiffhist.last_upd) AND (futquotesdiffhist.last_upd > (now() - '00:15:00'::interval)))
  GROUP BY futquotesdiffhist.code
 HAVING (min(futquotesdiffhist.bid) > (0)::double precision);


ALTER TABLE public.diffhistview_1510 OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 263058)
-- Name: diffhistview_t1510; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview_t1510 AS
 SELECT df_all_candles_t.security AS code,
    df_all_candles_t.class_code AS board,
    min(df_all_candles_t.low) AS min,
    max(df_all_candles_t.high) AS max,
    avg(df_all_candles_t.close) AS mean,
    sum(df_all_candles_t.volume) AS volume,
    count(*) AS count
   FROM public.df_all_candles_t
  WHERE (((now() - '00:05:00'::interval) > df_all_candles_t.datetime) AND (df_all_candles_t.datetime > (now() - '00:15:00'::interval)))
  GROUP BY df_all_candles_t.security, df_all_candles_t.class_code
 HAVING (min(df_all_candles_t.low) > (0)::double precision);


ALTER TABLE public.diffhistview_t1510 OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 65504)
-- Name: futquotesdiff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.futquotesdiff (
    code character varying(16),
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
    last_upd timestamp with time zone
);


ALTER TABLE public.futquotesdiff OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 24637)
-- Name: futquoteshist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.futquoteshist (
    fullid character varying(128),
    code character varying(16),
    status character varying(16),
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
    maturitydate character varying(16),
    tradedate character varying(12),
    closeprice double precision,
    prctchange double precision,
    instrumentid character varying(32),
    lot integer,
    prec integer,
    pricestep double precision,
    lastdealqty bigint,
    lastdealvol double precision,
    pricestepcur double precision,
    updated_at timestamp with time zone,
    snaptimestamp timestamp with time zone DEFAULT now()
);


ALTER TABLE public.futquoteshist OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 130580)
-- Name: jumps; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.jumps AS
 SELECT df.code,
    df.bid,
    df.bidamount,
    df.ask,
    df.askamount,
    df.openinterest,
    df.volume,
    df.volume_inc,
    df.bid_inc,
    df.ask_inc,
    df.updated_at,
    df.last_upd,
    st.index,
    st.security,
    st.max_volume,
    st.spread,
    st.dt,
    st.cnt,
    now() AS now
   FROM (public.futquotesdiff df
     LEFT JOIN public.df_stats st ON (((df.code)::text = st.security)))
  WHERE ((df.volume_inc > (st.max_volume)::double precision) AND (abs((df.bid_inc + df.ask_inc)) > ((2)::double precision * st.spread)) AND (st.dt > (now() - '00:10:00'::interval)));


ALTER TABLE public.jumps OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24642)
-- Name: monitor_sec; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monitor_sec (
    code character varying(32) NOT NULL,
    current_zone character varying(32),
    previous_zone character varying(32),
    upper_bound double precision,
    lower_bound double precision,
    price double precision,
    std double precision,
    last_state_change timestamp without time zone
);


ALTER TABLE public.monitor_sec OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 138997)
-- Name: order_discovery; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_discovery (
    code character varying(32),
    date_discovery timestamp with time zone,
    channel_source character varying(32),
    news_time timestamp with time zone,
    min_val double precision,
    max_val double precision,
    mean_val double precision,
    volume double precision
);


ALTER TABLE public.order_discovery OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 44514)
-- Name: orders_auto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_auto (
    code character varying(16),
    market character varying(16),
    amount bigint,
    "limit" double precision,
    executed bigint,
    lastorder bigint,
    maxspreadprc double precision,
    id integer NOT NULL,
    strategy character varying(16)
);


ALTER TABLE public.orders_auto OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 44835)
-- Name: orders_auto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_auto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_auto_id_seq OWNER TO postgres;

--
-- TOC entry 3585 (class 0 OID 0)
-- Dependencies: 229
-- Name: orders_auto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_auto_id_seq OWNED BY public.orders_auto.id;


--
-- TOC entry 244 (class 1259 OID 130513)
-- Name: orders_my_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_my_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_my_id_seq OWNER TO postgres;

--
-- TOC entry 3586 (class 0 OID 0)
-- Dependencies: 244
-- Name: orders_my_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_my_id_seq OWNED BY public.orders_my.id;


--
-- TOC entry 227 (class 1259 OID 36980)
-- Name: pos_eq; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pos_eq (
    instrument character varying(32),
    pos bigint,
    price double precision,
    volume double precision,
    pnl double precision,
    buy bigint,
    sell bigint,
    tobuy bigint,
    tosell bigint,
    firm character varying(32),
    account character varying(32),
    client_id character varying(32),
    settlement character varying(4),
    code character varying(16)
);


ALTER TABLE public.pos_eq OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 36409)
-- Name: pos_fut; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pos_fut (
    code character varying(16),
    instrument character varying(32),
    maturity date,
    pos bigint,
    buy bigint,
    sell bigint,
    pnl double precision,
    price_balance double precision,
    firm character varying(16),
    account character varying(16),
    type character varying(16)
);


ALTER TABLE public.pos_fut OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 98254)
-- Name: quote_bollinger; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.quote_bollinger AS
 SELECT q.code,
    b.class_code,
    q.quote,
    ((q.quote - b.mean) / b.std) AS bollinger,
    b.count,
    b.up,
    b.down
   FROM (( SELECT futquotesdiff.code,
            ((futquotesdiff.bid + futquotesdiff.ask) / (2)::double precision) AS quote
           FROM public.futquotesdiff
        UNION ALL
         SELECT secquotes.code,
            ((secquotes.bid + secquotes.ask) / (2)::double precision)
           FROM public.secquotes) q
     JOIN public.df_bollinger b ON (((q.code)::text = b.security)))
  WHERE (q.quote > (0)::double precision)
  ORDER BY ((q.quote - b.mean) / b.std) DESC;


ALTER TABLE public.quote_bollinger OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 98150)
-- Name: united_pos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.united_pos AS
 SELECT pos_fut.code,
    pos_fut.pos,
    pos_fut.buy,
    pos_fut.sell,
    pos_fut.pnl,
    pos_fut.price_balance,
    (((pos_fut.pos)::double precision * pos_fut.price_balance) + pos_fut.pnl) AS volume,
    pos_fut.firm
   FROM public.pos_fut
  WHERE (((abs(pos_fut.pos) + pos_fut.buy) + pos_fut.sell) <> 0)
UNION ALL
 SELECT pos_eq.code,
    pos_eq.pos,
    pos_eq.buy,
    pos_eq.sell,
    pos_eq.pnl,
    pos_eq.price AS price_balance,
    (pos_eq.volume + pos_eq.pnl) AS volume,
    'TQBR'::character varying AS firm
   FROM public.pos_eq
  WHERE (((abs(pos_eq.pos) + pos_eq.buy) + pos_eq.sell) <> 0);


ALTER TABLE public.united_pos OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 98289)
-- Name: pos_bollinger; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.pos_bollinger AS
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
   FROM (public.quote_bollinger b
     JOIN public.united_pos p ON (((b.code)::text = (p.code)::text)));


ALTER TABLE public.pos_bollinger OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 139034)
-- Name: secquotesdiff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secquotesdiff (
    code character varying(16),
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    volume double precision,
    volume_inc double precision,
    bid_inc double precision,
    ask_inc double precision,
    updated_at timestamp with time zone,
    last_upd timestamp with time zone
);


ALTER TABLE public.secquotesdiff OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24650)
-- Name: secquoteshist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secquoteshist (
    fullid character varying(128),
    instrumentid character varying(32),
    type character varying(16),
    code character varying(16),
    tradedate character varying(12),
    currency character varying(8),
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    lastprice double precision,
    volume double precision,
    prctchange double precision,
    lastdealtime character varying(32),
    session character varying(32),
    listing integer,
    valuedate character varying(16),
    isin character varying(16),
    "timestamp" time with time zone,
    snaptimestamp time with time zone DEFAULT now(),
    lot integer,
    prec bigint,
    pricestep double precision,
    lastdealqty double precision,
    lastdealvol double precision,
    updated_at timestamp with time zone
);


ALTER TABLE public.secquoteshist OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 263079)
-- Name: signal; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.signal AS
 SELECT now() AS tstz,
    od.code,
    od.date_discovery,
    od.channel_source,
    od.news_time,
    od.min_val,
    od.max_val,
    od.mean_val,
    od.volume,
    dhv.board,
    dhv.min,
    dhv.max,
    dhv.volume AS last_volume,
    dhv.count
   FROM (public.order_discovery od
     JOIN public.diffhistview dhv ON (((od.code)::text = (dhv.code)::text)))
  WHERE (((dhv.max - dhv.min) > (od.max_val - od.min_val)) AND (dhv.volume > od.volume) AND (now() < (od.news_time + '00:05:00'::interval)));


ALTER TABLE public.signal OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 263073)
-- Name: signal_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.signal_arch (
    id integer NOT NULL,
    tstz timestamp with time zone,
    code character varying(16),
    date_discovery timestamp with time zone,
    channel_source character varying(64),
    news_time timestamp with time zone,
    min_val double precision,
    max_val double precision,
    mean_val double precision,
    volume double precision,
    board character varying(32),
    min double precision,
    max double precision,
    last_volume double precision,
    count bigint
);


ALTER TABLE public.signal_arch OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 263072)
-- Name: signal_arch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.signal_arch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.signal_arch_id_seq OWNER TO postgres;

--
-- TOC entry 3587 (class 0 OID 0)
-- Dependencies: 258
-- Name: signal_arch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.signal_arch_id_seq OWNED BY public.signal_arch.id;


--
-- TOC entry 264 (class 1259 OID 322196)
-- Name: tinkoff_params; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tinkoff_params (
    index bigint,
    name text,
    ticker text,
    class_code text,
    figi text,
    type text,
    min_price_increment text,
    currency text,
    exchange text
);


ALTER TABLE public.tinkoff_params OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 24655)
-- Name: vpnl; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vpnl AS
 SELECT d."time",
    (
        CASE
            WHEN ((d.bs)::text = 'BUY'::text) THEN 1
            ELSE '-1'::integer
        END * d.amount) AS amount,
    d.code,
    d.price AS in_price,
    q.price,
    d.volume,
    d.broker_fees,
    ((((
        CASE
            WHEN ((d.bs)::text = 'BUY'::text) THEN 1
            ELSE '-1'::integer
        END)::double precision * d.volume) * ((q.price / d.price) - (1)::double precision)) - d.broker_fees) AS pnl,
    q.lot
   FROM (public.deals d
     JOIN ( SELECT futquotes.code,
            ((futquotes.bid + futquotes.ask) / (2)::double precision) AS price,
            1 AS lot
           FROM public.futquotes
          WHERE (futquotes.bid > (0)::double precision)
        UNION ALL
         SELECT secquotes.code,
            ((secquotes.bid + secquotes.ask) / (2)::double precision) AS price,
            secquotes.lot
           FROM public.secquotes
          WHERE (secquotes.bid > (0)::double precision)) q ON (((d.code)::text = (q.code)::text)));


ALTER TABLE public.vpnl OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24660)
-- Name: vpnlext; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vpnlext AS
 SELECT l.amount,
    l.code,
    l.mprice,
    l.pnl,
    (((l.amount)::double precision * l.mprice) * (l.lot)::double precision) AS volume,
        CASE
            WHEN (l.amount = (0)::numeric) THEN (0)::double precision
            ELSE (((l.mprice * (l.lot)::double precision) - l.pnl) / (l.amount)::double precision)
        END AS breakevenprice
   FROM ( SELECT sum(vpnl.amount) AS amount,
            vpnl.code,
            avg(vpnl.price) AS mprice,
            sum(vpnl.pnl) AS pnl,
            avg(vpnl.lot) AS lot
           FROM public.vpnl
          GROUP BY vpnl.code) l;


ALTER TABLE public.vpnlext OWNER TO postgres;

--
-- TOC entry 3378 (class 2604 OID 44836)
-- Name: orders_auto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_auto ALTER COLUMN id SET DEFAULT nextval('public.orders_auto_id_seq'::regclass);


--
-- TOC entry 3376 (class 2604 OID 130514)
-- Name: orders_my id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_my ALTER COLUMN id SET DEFAULT nextval('public.orders_my_id_seq'::regclass);


--
-- TOC entry 3379 (class 2604 OID 263076)
-- Name: signal_arch id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signal_arch ALTER COLUMN id SET DEFAULT nextval('public.signal_arch_id_seq'::regclass);


--
-- TOC entry 3400 (class 2606 OID 155465)
-- Name: df_all_candles_t_arch candles_t_arch_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t_arch
    ADD CONSTRAINT candles_t_arch_constr UNIQUE (security, datetime);


--
-- TOC entry 3407 (class 2606 OID 155467)
-- Name: df_all_candles_t candles_t_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t
    ADD CONSTRAINT candles_t_constr UNIQUE (security, datetime);


--
-- TOC entry 3402 (class 2606 OID 139044)
-- Name: df_all_candles_t_arch df_all_candles_t_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t_arch
    ADD CONSTRAINT df_all_candles_t_arch_pkey PRIMARY KEY (security, datetime, open, high, low, close, volume);


--
-- TOC entry 3381 (class 2606 OID 24666)
-- Name: monitor_sec monitor_sec_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monitor_sec
    ADD CONSTRAINT monitor_sec_pkey PRIMARY KEY (code);


--
-- TOC entry 3385 (class 2606 OID 44841)
-- Name: orders_auto orders_auto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_auto
    ADD CONSTRAINT orders_auto_pkey PRIMARY KEY (id);


--
-- TOC entry 3383 (class 2606 OID 130520)
-- Name: orders_my orders_my_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_my
    ADD CONSTRAINT orders_my_pkey PRIMARY KEY (id);


--
-- TOC entry 3411 (class 2606 OID 263078)
-- Name: signal_arch signal_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signal_arch
    ADD CONSTRAINT signal_arch_pkey PRIMARY KEY (id);


--
-- TOC entry 3408 (class 1259 OID 322210)
-- Name: idx_candles_datetime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candles_datetime ON public.df_all_candles_t USING btree (datetime DESC);


--
-- TOC entry 3409 (class 1259 OID 155462)
-- Name: idx_candles_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candles_security ON public.df_all_candles_t USING btree (security);


--
-- TOC entry 3388 (class 1259 OID 322209)
-- Name: idx_futquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_futquoteshist_lastupd ON public.futquotesdiffhist USING btree (last_upd DESC);


--
-- TOC entry 3389 (class 1259 OID 288215)
-- Name: idx_futquoteshit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_futquoteshit ON public.futquotesdiffhist USING btree (code);


--
-- TOC entry 3398 (class 1259 OID 322207)
-- Name: idx_ord_disc_code_nt; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ord_disc_code_nt ON public.order_discovery USING btree (code, news_time DESC);


--
-- TOC entry 3404 (class 1259 OID 155483)
-- Name: idx_secquoteshist; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_secquoteshist ON public.secquotesdiffhist USING btree (code);


--
-- TOC entry 3405 (class 1259 OID 322208)
-- Name: idx_secquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_secquoteshist_lastupd ON public.secquotesdiffhist USING btree (last_upd DESC);


--
-- TOC entry 3403 (class 1259 OID 155463)
-- Name: idx_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_security ON public.df_all_candles_t_arch USING btree (security);


--
-- TOC entry 3391 (class 1259 OID 112451)
-- Name: ix_df_all_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_all_levels_index ON public.df_all_levels USING btree (index);


--
-- TOC entry 3392 (class 1259 OID 112462)
-- Name: ix_df_all_volumes_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_all_volumes_index ON public.df_all_volumes USING btree (index);


--
-- TOC entry 3386 (class 1259 OID 97825)
-- Name: ix_df_bollinger_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_bollinger_index ON public.df_bollinger USING btree (index);


--
-- TOC entry 3397 (class 1259 OID 130590)
-- Name: ix_df_jumps_level_0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_jumps_level_0 ON public.df_jumps USING btree (level_0);


--
-- TOC entry 3390 (class 1259 OID 112445)
-- Name: ix_df_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_levels_index ON public.df_levels USING btree (index);


--
-- TOC entry 3393 (class 1259 OID 113095)
-- Name: ix_df_monitor_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_monitor_index ON public.df_monitor USING btree (index);


--
-- TOC entry 3396 (class 1259 OID 130567)
-- Name: ix_df_stats_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_stats_index ON public.df_stats USING btree (index);


--
-- TOC entry 3387 (class 1259 OID 97831)
-- Name: ix_df_volumes_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_volumes_index ON public.df_volumes USING btree (index);


--
-- TOC entry 3394 (class 1259 OID 114129)
-- Name: ix_orders_in_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_in_index ON public.orders_in USING btree (index);


--
-- TOC entry 3395 (class 1259 OID 114135)
-- Name: ix_orders_out_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_out_index ON public.orders_out USING btree (index);


--
-- TOC entry 3413 (class 1259 OID 322201)
-- Name: ix_tinkoff_params_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tinkoff_params_index ON public.tinkoff_params USING btree (index);


--
-- TOC entry 3412 (class 1259 OID 322211)
-- Name: signal_arch_tstz; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX signal_arch_tstz ON public.signal_arch USING btree (tstz DESC);


--
-- TOC entry 3414 (class 2620 OID 24675)
-- Name: secquotes bigdealshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER bigdealshisttrigger AFTER UPDATE ON public.secquotes FOR EACH ROW EXECUTE FUNCTION public.bigdealhistupd();


--
-- TOC entry 3419 (class 2620 OID 109108)
-- Name: futquotesdiff futquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER futquotesdiffhist_upd AFTER INSERT OR UPDATE ON public.futquotesdiff FOR EACH ROW EXECUTE FUNCTION public.futquotesdiffhistupd();


--
-- TOC entry 3417 (class 2620 OID 24676)
-- Name: futquotes futquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER futquoteshisttrigger AFTER UPDATE ON public.futquotes FOR EACH ROW EXECUTE FUNCTION public.futquoteshistupd();


--
-- TOC entry 3420 (class 2620 OID 109048)
-- Name: futquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER last_upd_rule BEFORE INSERT OR UPDATE ON public.futquotesdiff FOR EACH ROW EXECUTE FUNCTION public.last_upd_upd();


--
-- TOC entry 3421 (class 2620 OID 139040)
-- Name: secquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER last_upd_rule BEFORE INSERT OR UPDATE ON public.secquotesdiff FOR EACH ROW EXECUTE FUNCTION public.last_upd_upd();


--
-- TOC entry 3422 (class 2620 OID 139042)
-- Name: secquotesdiff secquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER secquotesdiffhist_upd AFTER INSERT OR UPDATE ON public.secquotesdiff FOR EACH ROW EXECUTE FUNCTION public.secquotesdiffhistupd();


--
-- TOC entry 3415 (class 2620 OID 24677)
-- Name: secquotes secquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER secquoteshisttrigger AFTER UPDATE ON public.secquotes FOR EACH ROW EXECUTE FUNCTION public.secquoteshistupd();


--
-- TOC entry 3418 (class 2620 OID 108819)
-- Name: futquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER updated_at_rule BEFORE INSERT OR UPDATE ON public.futquotes FOR EACH ROW EXECUTE FUNCTION public.updated_at_upd();


--
-- TOC entry 3416 (class 2620 OID 108826)
-- Name: secquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER updated_at_rule BEFORE INSERT OR UPDATE ON public.secquotes FOR EACH ROW EXECUTE FUNCTION public.updated_at_upd();


-- Completed on 2023-06-10 04:38:35 MSK

--
-- PostgreSQL database dump complete
--

