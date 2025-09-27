--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.4 (Ubuntu 15.4-1.pgdg22.04+1)

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
-- Name: test; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE test WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';


ALTER DATABASE test OWNER TO postgres;

\connect test

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
-- Name: futquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.futquotesdiffhistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO futquotesdiffhist(code, bid, bidamount, ask, askamount, openinterest, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.openinterest, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd, NEW.volume_wa, NEW.min_5mins, NEW.max_5mins);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.futquotesdiffhistupd() OWNER TO postgres;

--
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
-- Name: secquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.secquotesdiffhistupd() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    INSERT INTO secquotesdiffhist(code, bid, bidamount, ask, askamount, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd, new.volume_wa, new.min_5mins, new.max_5mins);

RETURN NEW;

END;

$$;


ALTER FUNCTION public.secquotesdiffhistupd() OWNER TO postgres;

--
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
-- Name: orders_in_tcs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_in_tcs (
    index bigint,
    quantity bigint,
    direction bigint,
    account_id text,
    order_type bigint,
    order_id text,
    instrument_id text,
    last_upd timestamp without time zone,
    comment text,
    code text
);


ALTER TABLE public.orders_in_tcs OWNER TO postgres;

--
-- Name: orders_out_tcs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_out_tcs (
    index bigint,
    order_id text,
    order_id_in text,
    execution_report_status bigint,
    lots_requested bigint,
    lots_executed bigint,
    figi text,
    direction bigint,
    order_type bigint,
    message text,
    instrument_uid text,
    initial_order_price text,
    executed_order_price text,
    total_order_amount text,
    initial_commission text,
    executed_commission text,
    aci_value text,
    initial_security_price text,
    initial_order_price_pt text,
    code text,
    comment text
);


ALTER TABLE public.orders_out_tcs OWNER TO postgres;

--
-- Name: autoorders_tcs; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.autoorders_tcs AS
 SELECT intcs.quantity,
    intcs.direction,
    intcs.account_id,
    intcs.order_type,
    intcs.order_id,
    intcs.instrument_id,
    intcs.last_upd,
    intcs.comment,
    intcs.code,
    outtcs.order_id AS order_id_out,
    outtcs.execution_report_status,
    outtcs.lots_requested,
    outtcs.lots_executed,
    COALESCE((intcs.quantity - outtcs.lots_requested), intcs.quantity) AS unconfirmed_amount,
    outtcs.message,
    outtcs.initial_order_price,
    outtcs.executed_order_price,
    outtcs.total_order_amount,
    outtcs.initial_commission,
    outtcs.executed_commission,
    outtcs.initial_security_price,
    outtcs.initial_order_price_pt
   FROM (public.orders_in_tcs intcs
     LEFT JOIN public.orders_out_tcs outtcs ON ((intcs.order_id = outtcs.order_id_in)));


ALTER TABLE public.autoorders_tcs OWNER TO postgres;

--
-- Name: autoorders_grouped_tcs; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.autoorders_grouped_tcs AS
 SELECT autoorders_tcs.code,
    autoorders_tcs.comment,
    sum((COALESCE(autoorders_tcs.lots_executed, (0)::bigint) *
        CASE
            WHEN (autoorders_tcs.direction = 1) THEN 1
            ELSE '-1'::integer
        END)) AS amount,
    sum((COALESCE(autoorders_tcs.unconfirmed_amount, (0)::bigint) *
        CASE
            WHEN (autoorders_tcs.direction = 1) THEN 1
            ELSE '-1'::integer
        END)) AS unconfirmed_amount,
    sum(((COALESCE(autoorders_tcs.lots_requested, (0)::bigint) - COALESCE(autoorders_tcs.lots_executed, (0)::bigint)) *
        CASE
            WHEN (autoorders_tcs.direction = 1) THEN 1
            ELSE '-1'::integer
        END)) AS amount_pending
   FROM public.autoorders_tcs
  GROUP BY autoorders_tcs.code, autoorders_tcs.comment;


ALTER TABLE public.autoorders_grouped_tcs OWNER TO postgres;

--
-- Name: diffhist_t5; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.diffhist_t5 (
    index bigint,
    code text,
    board text,
    min double precision,
    max double precision,
    mean double precision,
    volume bigint,
    count bigint,
    min_datetime timestamp with time zone,
    max_datetime timestamp with time zone
);


ALTER TABLE public.diffhist_t5 OWNER TO postgres;

--
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
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision
);


ALTER TABLE public.futquotesdiff OWNER TO postgres;

--
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
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision
);


ALTER TABLE public.secquotesdiff OWNER TO postgres;

--
-- Name: diffminmax; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffminmax AS
 SELECT t.code,
    t.board,
    min(t.min) AS min_5mins,
    max(t.max) AS max_5mins
   FROM ( SELECT diffhist_t5.code,
            diffhist_t5.board,
            diffhist_t5.min,
            diffhist_t5.max
           FROM public.diffhist_t5
        UNION ALL
         SELECT futquotesdiff.code,
            'SPBFUT'::text,
            futquotesdiff.min_5mins,
            futquotesdiff.max_5mins
           FROM public.futquotesdiff
        UNION ALL
         SELECT secquotesdiff.code,
            'TQBR'::text,
            secquotesdiff.min_5mins,
            secquotesdiff.max_5mins
           FROM public.secquotesdiff) t
  WHERE ((t.min IS NOT NULL) AND (t.max IS NOT NULL))
  GROUP BY t.code, t.board;


ALTER TABLE public.diffminmax OWNER TO postgres;

--
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
-- Name: orders_my; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_my (
    id integer NOT NULL,
    activate_news integer,
    activate_jump integer,
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
    start_time timestamp with time zone,
    provider character varying(8),
    order_type character varying(8),
    barrier_bound double precision
);


ALTER TABLE public.orders_my OWNER TO postgres;

--
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
    ord.activate_news,
    ord.activate_jump,
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
    COALESCE((executed.amount_pending)::integer, 0) AS amount_pending,
    ord.start_time,
    ord.end_time,
    ord.provider,
    minmax.min_5mins,
    minmax.max_5mins,
    ord.order_type,
    ord.barrier_bound
   FROM (((( SELECT futquotes.code,
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
            orders_my.activate_news,
            orders_my.activate_jump,
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
           FROM public.orders_my) ord ON (((allquotes.code)::text = (ord.code)::text)))
     LEFT JOIN ( SELECT autoorders_grouped.code,
            autoorders_grouped.comment,
            autoorders_grouped.amount,
            autoorders_grouped.unconfirmed_amount,
            autoorders_grouped.amount_pending,
            NULL::text AS provider
           FROM public.autoorders_grouped
        UNION ALL
         SELECT autoorders_grouped_tcs.code,
            autoorders_grouped_tcs.comment,
            autoorders_grouped_tcs.amount,
            autoorders_grouped_tcs.unconfirmed_amount,
            autoorders_grouped_tcs.amount_pending,
            'tcs'::text AS provider
           FROM public.autoorders_grouped_tcs) executed ON (((executed.code = (ord.code)::text) AND (concat((ord.comment)::text, ord.id) = executed.comment) AND ((COALESCE(ord.provider, ''::character varying))::text = COALESCE(executed.provider, ''::text)))))
     LEFT JOIN ( SELECT diffminmax.code,
            diffminmax.min_5mins,
            diffminmax.max_5mins
           FROM public.diffminmax) minmax ON (((allquotes.code)::text = minmax.code)));


ALTER TABLE public.allquotes OWNER TO postgres;

--
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
-- Name: analytics_beta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_beta (
    index bigint,
    sec text,
    base_asset text,
    beta double precision,
    r2 double precision,
    corr double precision
);


ALTER TABLE public.analytics_beta OWNER TO postgres;

--
-- Name: analytics_future; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_future (
    index bigint,
    ds timestamp without time zone,
    yhat_lower double precision,
    yhat_upper double precision,
    yhat double precision,
    sigma double precision,
    trend_abs double precision,
    trend_rel_pct double precision,
    sec text
);


ALTER TABLE public.analytics_future OWNER TO postgres;

--
-- Name: analytics_past; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_past (
    index bigint,
    additive_terms double precision,
    wd integer,
    dt time without time zone,
    additive_terms_prct double precision,
    sec text
);


ALTER TABLE public.analytics_past OWNER TO postgres;

--
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
-- Name: diffhist_t1510; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.diffhist_t1510 (
    index bigint,
    code text,
    board text,
    min double precision,
    max double precision,
    mean double precision,
    volume bigint,
    count bigint,
    min_datetime timestamp with time zone,
    max_datetime timestamp with time zone
);


ALTER TABLE public.diffhist_t1510 OWNER TO postgres;

--
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
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision
);


ALTER TABLE public.futquotesdiffhist OWNER TO postgres;

--
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
    last_upd timestamp with time zone,
    volume_wa double precision,
    min_5mins double precision,
    max_5mins double precision
);


ALTER TABLE public.secquotesdiffhist OWNER TO postgres;

--
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
-- Name: diffhistview_5; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview_5 AS
 SELECT secquotesdiffhist.code,
    'TQBR'::text AS board,
    min(secquotesdiffhist.ask) AS min,
    max(secquotesdiffhist.bid) AS max,
    avg(((secquotesdiffhist.bid + secquotesdiffhist.ask) / (2)::double precision)) AS mean,
    sum(secquotesdiffhist.volume_inc) AS volume,
    count(*) AS count,
    min(secquotesdiffhist.last_upd) AS min_datetime,
    max(secquotesdiffhist.last_upd) AS max_datetime
   FROM public.secquotesdiffhist
  WHERE ((secquotesdiffhist.last_upd > (now() - '00:05:00'::interval)) AND (secquotesdiffhist.bid > (0)::double precision))
  GROUP BY secquotesdiffhist.code
 HAVING (min(secquotesdiffhist.bid) > (0)::double precision)
UNION ALL
 SELECT futquotesdiffhist.code,
    'SPBFUT'::text AS board,
    min(futquotesdiffhist.ask) AS min,
    max(futquotesdiffhist.bid) AS max,
    avg(((futquotesdiffhist.bid + futquotesdiffhist.ask) / (2)::double precision)) AS mean,
    sum(futquotesdiffhist.volume_inc) AS volume,
    count(*) AS count,
    min(futquotesdiffhist.last_upd) AS min_datetime,
    max(futquotesdiffhist.last_upd) AS max_datetime
   FROM public.futquotesdiffhist
  WHERE ((futquotesdiffhist.last_upd > (now() - '00:05:00'::interval)) AND (futquotesdiffhist.bid > (0)::double precision))
  GROUP BY futquotesdiffhist.code
 HAVING (min(futquotesdiffhist.bid) > (0)::double precision);


ALTER TABLE public.diffhistview_5 OWNER TO postgres;

--
-- Name: diffhistview_t1510; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview_t1510 AS
 SELECT df_all_candles_t.security AS code,
    df_all_candles_t.class_code AS board,
    min(df_all_candles_t.low) AS min,
    max(df_all_candles_t.high) AS max,
    avg(df_all_candles_t.close) AS mean,
    sum(df_all_candles_t.volume) AS volume,
    count(*) AS count,
    min(df_all_candles_t.datetime) AS min_datetime,
    max(df_all_candles_t.datetime) AS max_datetime
   FROM public.df_all_candles_t
  WHERE (((now() - '00:05:00'::interval) > df_all_candles_t.datetime) AND (df_all_candles_t.datetime > (now() - '00:15:00'::interval)))
  GROUP BY df_all_candles_t.security, df_all_candles_t.class_code
 HAVING (min(df_all_candles_t.low) > (0)::double precision);


ALTER TABLE public.diffhistview_t1510 OWNER TO postgres;

--
-- Name: diffhistview_t5; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.diffhistview_t5 AS
 SELECT df_all_candles_t.security AS code,
    df_all_candles_t.class_code AS board,
    min(df_all_candles_t.low) AS min,
    max(df_all_candles_t.high) AS max,
    avg(df_all_candles_t.close) AS mean,
    sum(df_all_candles_t.volume) AS volume,
    count(*) AS count,
    min(df_all_candles_t.datetime) AS min_datetime,
    max(df_all_candles_t.datetime) AS max_datetime
   FROM public.df_all_candles_t
  WHERE ((now() - '00:05:00'::interval) <= df_all_candles_t.datetime)
  GROUP BY df_all_candles_t.security, df_all_candles_t.class_code
 HAVING (min(df_all_candles_t.low) > (0)::double precision);


ALTER TABLE public.diffhistview_t5 OWNER TO postgres;

--
-- Name: event_news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_news (
    code character varying(32),
    date_discovery timestamp with time zone,
    channel_source character varying(32),
    news_time timestamp with time zone,
    keyword character varying(32),
    msg text
);


ALTER TABLE public.event_news OWNER TO postgres;

--
-- Name: events_jumps_hist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events_jumps_hist (
    index bigint,
    code text,
    min double precision,
    max double precision,
    mean double precision,
    volume bigint,
    count bigint,
    bid double precision,
    bidamount double precision,
    ask double precision,
    askamount double precision,
    volume_inc double precision,
    bid_inc double precision,
    ask_inc double precision,
    updated_at timestamp with time zone,
    last_upd timestamp with time zone,
    volume_wa double precision,
    process_time timestamp with time zone,
    jump_prct double precision,
    out_prct double precision,
    volume_peak double precision,
    out_std double precision
);


ALTER TABLE public.events_jumps_hist OWNER TO postgres;

--
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
-- Name: jump_events; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.jump_events AS
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
    (((fq.bid_inc + fq.ask_inc) / (fq.bid + fq.ask)) * (100)::double precision) AS jump_prct,
        CASE
            WHEN (fq.ask < dh.min) THEN ((- ((dh.min / fq.ask) - (1)::double precision)) * (100)::double precision)
            ELSE (((fq.bid / dh.max) - (1)::double precision) * (100)::double precision)
        END AS out_prct,
    round((((fq.volume_inc * (10)::double precision) / (dh.volume)::double precision) * dh.max)) AS volume_peak,
        CASE
            WHEN (fq.ask < dh.min) THEN ((fq.ask - dh.min) / (dh.max - dh.min))
            ELSE ((fq.bid - dh.max) / (dh.max - dh.min))
        END AS out_std
   FROM (public.diffhist_t1510 dh
     JOIN public.futquotesdiff fq ON ((dh.code = (fq.code)::text)))
  WHERE (((((dh.volume)::double precision * dh.max) / (10)::double precision) < fq.volume_inc) AND ((fq.ask < dh.min) OR (fq.bid > dh.max)) AND (fq.bid > (0)::double precision));


ALTER TABLE public.jump_events OWNER TO postgres;

--
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
-- Name: orders_auto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_auto_id_seq OWNED BY public.orders_auto.id;


--
-- Name: orders_event_activator; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_event_activator (
    id bigint NOT NULL,
    ticker character varying(16),
    keyword character varying(16),
    start_date timestamp with time zone DEFAULT now(),
    end_date timestamp with time zone DEFAULT (now() + '00:00:01'::interval),
    is_activated boolean DEFAULT false,
    activate_time timestamp with time zone,
    channel_source character varying(32) DEFAULT 'markettwits'::character varying
);


ALTER TABLE public.orders_event_activator OWNER TO postgres;

--
-- Name: orders_event_activator_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_event_activator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_event_activator_id_seq OWNER TO postgres;

--
-- Name: orders_event_activator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_event_activator_id_seq OWNED BY public.orders_event_activator.id;


--
-- Name: orders_event_activator_jumps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders_event_activator_jumps (
    id bigint NOT NULL,
    ticker character varying(16) NOT NULL,
    start_date timestamp with time zone DEFAULT now() NOT NULL,
    end_date timestamp with time zone DEFAULT (now() + '00:00:01'::interval) NOT NULL,
    is_activated boolean DEFAULT false NOT NULL,
    orders_my_id integer NOT NULL,
    jump_prct double precision,
    out_prct double precision,
    volume_peak double precision,
    out_std double precision,
    activate_time timestamp with time zone
);


ALTER TABLE public.orders_event_activator_jumps OWNER TO postgres;

--
-- Name: orders_event_activator_jumps_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_event_activator_jumps_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_event_activator_jumps_id_seq OWNER TO postgres;

--
-- Name: orders_event_activator_jumps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_event_activator_jumps_id_seq OWNED BY public.orders_event_activator_jumps.id;


--
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
-- Name: orders_my_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_my_id_seq OWNED BY public.orders_my.id;


--
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
-- Name: signal_arch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.signal_arch_id_seq OWNED BY public.signal_arch.id;


--
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
-- Name: trd_pos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.trd_pos AS
 SELECT 1 AS state,
    1 AS quantity,
    ('POS'::text || mntr.code) AS comment,
        CASE
            WHEN (lvls.down = '0'::text) THEN (lvls.mid - ((4)::double precision * lvls.std))
            ELSE lvls.sl
        END AS stop_loss,
    lvls."end" AS take_profit,
    lvls.max_start AS barrier,
    1 AS max_amount,
    1 AS pause,
    mntr.code,
    1 AS direction,
    (now() + '00:01:00'::interval) AS end_time,
    now() AS start_time,
    mntr.new_state,
    mntr.new_price,
    mntr.new_start,
    mntr.new_end,
    lvls.std,
    lvls.price AS next_resistance,
    lvls.min_start AS prev_resistance_std,
    lvls.sl,
    lvls.mid AS prev_resistance,
    lvls.down AS preprev_resistance,
    lvls.prev_end AS prev_take_profit
   FROM (public.df_monitor mntr
     LEFT JOIN ( SELECT df_levels.index,
            df_levels.price,
            df_levels.volume,
            df_levels.std,
            df_levels.sec,
            df_levels.min_start,
            df_levels.max_start,
            df_levels."end",
            df_levels.sl,
            df_levels.mid,
            df_levels.down,
            df_levels.prev_end,
            df_levels.next_sl,
            df_levels.implied_prob,
            df_levels."timestamp"
           FROM public.df_levels
          WHERE (df_levels.max_start > df_levels.min_start)) lvls ON ((mntr.code = lvls.sec)))
  WHERE (("right"(mntr.code, 1) ~ '[0-9]'::text) AND (mntr.new_price >= mntr.old_price) AND (lvls.min_start <= mntr.new_price) AND (mntr.new_price <= lvls.max_start) AND (mntr.new_state = 'start'::text));


ALTER TABLE public.trd_pos OWNER TO postgres;

--
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
-- Name: orders_auto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_auto ALTER COLUMN id SET DEFAULT nextval('public.orders_auto_id_seq'::regclass);


--
-- Name: orders_event_activator id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_event_activator ALTER COLUMN id SET DEFAULT nextval('public.orders_event_activator_id_seq'::regclass);


--
-- Name: orders_event_activator_jumps id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_event_activator_jumps ALTER COLUMN id SET DEFAULT nextval('public.orders_event_activator_jumps_id_seq'::regclass);


--
-- Name: orders_my id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_my ALTER COLUMN id SET DEFAULT nextval('public.orders_my_id_seq'::regclass);


--
-- Name: signal_arch id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signal_arch ALTER COLUMN id SET DEFAULT nextval('public.signal_arch_id_seq'::regclass);


--
-- Name: df_all_candles_t_arch candles_t_arch_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t_arch
    ADD CONSTRAINT candles_t_arch_constr UNIQUE (security, datetime);


--
-- Name: df_all_candles_t candles_t_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t
    ADD CONSTRAINT candles_t_constr UNIQUE (security, datetime);


--
-- Name: df_all_candles_t_arch df_all_candles_t_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.df_all_candles_t_arch
    ADD CONSTRAINT df_all_candles_t_arch_pkey PRIMARY KEY (security, datetime, open, high, low, close, volume);


--
-- Name: orders_auto orders_auto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_auto
    ADD CONSTRAINT orders_auto_pkey PRIMARY KEY (id);


--
-- Name: orders_event_activator_jumps orders_event_activator_jumps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_event_activator_jumps
    ADD CONSTRAINT orders_event_activator_jumps_pkey PRIMARY KEY (id);


--
-- Name: orders_event_activator orders_event_activator_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_event_activator
    ADD CONSTRAINT orders_event_activator_pkey PRIMARY KEY (id);


--
-- Name: orders_my orders_my_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders_my
    ADD CONSTRAINT orders_my_pkey PRIMARY KEY (id);


--
-- Name: signal_arch signal_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signal_arch
    ADD CONSTRAINT signal_arch_pkey PRIMARY KEY (id);


--
-- Name: idx_candles_datetime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candles_datetime ON public.df_all_candles_t USING btree (datetime DESC);


--
-- Name: idx_candles_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candles_security ON public.df_all_candles_t USING btree (security);


--
-- Name: idx_futquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_futquoteshist_lastupd ON public.futquotesdiffhist USING btree (last_upd DESC);


--
-- Name: idx_futquoteshit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_futquoteshit ON public.futquotesdiffhist USING btree (code);


--
-- Name: idx_ord_disc_code_nt; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ord_disc_code_nt ON public.order_discovery USING btree (code, news_time DESC);


--
-- Name: idx_secquoteshist; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_secquoteshist ON public.secquotesdiffhist USING btree (code);


--
-- Name: idx_secquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_secquoteshist_lastupd ON public.secquotesdiffhist USING btree (last_upd DESC);


--
-- Name: idx_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_security ON public.df_all_candles_t_arch USING btree (security);


--
-- Name: ix_analytics_beta_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_beta_index ON public.analytics_beta USING btree (index);


--
-- Name: ix_analytics_future_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_future_index ON public.analytics_future USING btree (index);


--
-- Name: ix_analytics_past_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_past_index ON public.analytics_past USING btree (index);


--
-- Name: ix_df_all_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_all_levels_index ON public.df_all_levels USING btree (index);


--
-- Name: ix_df_all_volumes_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_all_volumes_index ON public.df_all_volumes USING btree (index);


--
-- Name: ix_df_bollinger_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_bollinger_index ON public.df_bollinger USING btree (index);


--
-- Name: ix_df_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_levels_index ON public.df_levels USING btree (index);


--
-- Name: ix_df_monitor_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_monitor_index ON public.df_monitor USING btree (index);


--
-- Name: ix_df_volumes_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_df_volumes_index ON public.df_volumes USING btree (index);


--
-- Name: ix_diffhist_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_diffhist_index ON public.diffhist_t1510 USING btree (index);


--
-- Name: ix_diffhist_t5_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_diffhist_t5_index ON public.diffhist_t5 USING btree (index);


--
-- Name: ix_events_jumps_hist_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_jumps_hist_index ON public.events_jumps_hist USING btree (index);


--
-- Name: ix_orders_in_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_in_index ON public.orders_in USING btree (index);


--
-- Name: ix_orders_in_tcs_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_in_tcs_index ON public.orders_in_tcs USING btree (index);


--
-- Name: ix_orders_out_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_out_index ON public.orders_out USING btree (index);


--
-- Name: ix_orders_out_tcs_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_out_tcs_index ON public.orders_out_tcs USING btree (index);


--
-- Name: ix_tinkoff_params_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tinkoff_params_index ON public.tinkoff_params USING btree (index);


--
-- Name: signal_arch_tstz; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX signal_arch_tstz ON public.signal_arch USING btree (tstz DESC);


--
-- Name: futquotesdiff futquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER futquotesdiffhist_upd AFTER INSERT OR UPDATE ON public.futquotesdiff FOR EACH ROW EXECUTE FUNCTION public.futquotesdiffhistupd();


--
-- Name: futquotes futquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER futquoteshisttrigger AFTER UPDATE ON public.futquotes FOR EACH ROW EXECUTE FUNCTION public.futquoteshistupd();


--
-- Name: futquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER last_upd_rule BEFORE INSERT OR UPDATE ON public.futquotesdiff FOR EACH ROW EXECUTE FUNCTION public.last_upd_upd();


--
-- Name: secquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER last_upd_rule BEFORE INSERT OR UPDATE ON public.secquotesdiff FOR EACH ROW EXECUTE FUNCTION public.last_upd_upd();


--
-- Name: secquotesdiff secquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER secquotesdiffhist_upd AFTER INSERT OR UPDATE ON public.secquotesdiff FOR EACH ROW EXECUTE FUNCTION public.secquotesdiffhistupd();


--
-- Name: secquotes secquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER secquoteshisttrigger AFTER UPDATE ON public.secquotes FOR EACH ROW EXECUTE FUNCTION public.secquoteshistupd();


--
-- Name: futquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER updated_at_rule BEFORE INSERT OR UPDATE ON public.futquotes FOR EACH ROW EXECUTE FUNCTION public.updated_at_upd();


--
-- Name: secquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER updated_at_rule BEFORE INSERT OR UPDATE ON public.secquotes FOR EACH ROW EXECUTE FUNCTION public.updated_at_upd();


--
-- PostgreSQL database dump complete
--

