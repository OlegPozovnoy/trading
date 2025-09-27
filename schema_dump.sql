--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Ubuntu 16.4-1.pgdg22.04+1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-1.pgdg22.04+1)

-- Started on 2024-08-26 19:33:21 MSK

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

DROP DATABASE IF EXISTS "test";
--
-- TOC entry 4398 (class 1262 OID 16388)
-- Name: test; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "test" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "test" OWNER TO "postgres";

\connect "test"

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
-- TOC entry 11 (class 2615 OID 34941)
-- Name: mos; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "mos";


ALTER SCHEMA "mos" OWNER TO "postgres";

--
-- TOC entry 4399 (class 0 OID 0)
-- Dependencies: 9
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- TOC entry 3 (class 3079 OID 16865)
-- Name: dblink; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "dblink" WITH SCHEMA "public";


--
-- TOC entry 4400 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION "dblink"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "dblink" IS 'connect to other PostgreSQL databases from within a database';


--
-- TOC entry 5 (class 3079 OID 146650)
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "public";


--
-- TOC entry 4401 (class 0 OID 0)
-- Dependencies: 5
-- Name: EXTENSION "pg_stat_statements"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "pg_stat_statements" IS 'track planning and execution statistics of all SQL statements executed';


--
-- TOC entry 4 (class 3079 OID 16911)
-- Name: postgres_fdw; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "postgres_fdw" WITH SCHEMA "public";


--
-- TOC entry 4402 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION "postgres_fdw"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "postgres_fdw" IS 'foreign-data wrapper for remote PostgreSQL servers';


--
-- TOC entry 6 (class 3079 OID 152901)
-- Name: system_stats; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "system_stats" WITH SCHEMA "public";


--
-- TOC entry 4403 (class 0 OID 0)
-- Dependencies: 6
-- Name: EXTENSION "system_stats"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "system_stats" IS 'EnterpriseDB system statistics for PostgreSQL';


--
-- TOC entry 2 (class 3079 OID 16389)
-- Name: tablefunc; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "tablefunc" WITH SCHEMA "public";


--
-- TOC entry 4404 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "tablefunc"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "tablefunc" IS 'functions that manipulate whole tables, including crosstab';


--
-- TOC entry 439 (class 1255 OID 16410)
-- Name: futquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."futquotesdiffhistupd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$

BEGIN

    INSERT INTO futquotesdiffhist(code, bid, bidamount, ask, askamount, openinterest, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.openinterest, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd, NEW.volume_wa, NEW.min_5mins, NEW.max_5mins);

RETURN NEW;

END;

$$;


ALTER FUNCTION "public"."futquotesdiffhistupd"() OWNER TO "postgres";

--
-- TOC entry 440 (class 1255 OID 16411)
-- Name: futquoteshistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."futquoteshistupd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
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


ALTER FUNCTION "public"."futquoteshistupd"() OWNER TO "postgres";

--
-- TOC entry 441 (class 1255 OID 16412)
-- Name: last_upd_upd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."last_upd_upd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_upd = now();
    RETURN NEW;   
END;
$$;


ALTER FUNCTION "public"."last_upd_upd"() OWNER TO "postgres";

--
-- TOC entry 442 (class 1255 OID 16413)
-- Name: secquotesdiffhistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."secquotesdiffhistupd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$

BEGIN

    INSERT INTO secquotesdiffhist(code, bid, bidamount, ask, askamount, volume, volume_inc, bid_inc, ask_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins)

         VALUES(NEW.code, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.volume, NEW.volume_inc, NEW.bid_inc, NEW.ask_inc, NEW.updated_at, NEW.last_upd, new.volume_wa, new.min_5mins, new.max_5mins);

RETURN NEW;

END;

$$;


ALTER FUNCTION "public"."secquotesdiffhistupd"() OWNER TO "postgres";

--
-- TOC entry 443 (class 1255 OID 16414)
-- Name: secquoteshistupd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."secquoteshistupd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$

BEGIN

    INSERT INTO secquoteshist ( fullid, instrumentid, type, code, tradedate, currency, bid, bidamount, ask, askamount, lastprice, volume, prctchange, lastdealtime, session, listing, valuedate, isin, updated_at, lot, prec, pricestep, lastdealqty, lastdealvol)

         VALUES(NEW.fullid, NEW.instrumentid, NEW.type, NEW.code, NEW.tradedate, NEW.currency, NEW.bid, NEW.bidamount, NEW.ask, NEW.askamount, NEW.lastprice, NEW.volume, NEW.prctchange, NEW.lastdealtime, NEW.session, NEW.listing, NEW.valuedate, NEW.isin, NEW.updated_at, NEW.lot, NEW.prec, NEW.pricestep, NEW.lastdealqty, NEW.lastdealvol);

RETURN NEW;

END;

$$;


ALTER FUNCTION "public"."secquoteshistupd"() OWNER TO "postgres";

--
-- TOC entry 444 (class 1255 OID 16415)
-- Name: updated_at_upd(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION "public"."updated_at_upd"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$BEGIN
    NEW.updated_at = now();
    RETURN NEW;   
END;
$$;


ALTER FUNCTION "public"."updated_at_upd"() OWNER TO "postgres";

--
-- TOC entry 2889 (class 1417 OID 17144)
-- Name: moscow; Type: SERVER; Schema: -; Owner: postgres
--

CREATE SERVER "moscow" FOREIGN DATA WRAPPER "postgres_fdw" OPTIONS (
    "dbname" 'test',
    "host" '10.8.0.3'
);


ALTER SERVER "moscow" OWNER TO "postgres";

--
-- TOC entry 4405 (class 0 OID 0)
-- Name: USER MAPPING postgres SERVER moscow; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR "postgres" SERVER "moscow" OPTIONS (
    "user" 'postgres'
);


--
-- TOC entry 283 (class 1259 OID 34942)
-- Name: allquotes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."allquotes" (
    "code" character varying(16),
    "market" "text",
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "mid" double precision,
    "id" integer,
    "activate_id" integer,
    "state" integer,
    "quantity" integer,
    "comment" character varying(128),
    "remains" integer,
    "stop_loss" double precision,
    "take_profit" double precision,
    "parent_id" integer,
    "barrier" double precision,
    "max_amount" integer,
    "pause" double precision,
    "direction" integer,
    "amount" integer,
    "unconfirmed_amount" integer,
    "amount_pending" integer,
    "start_time" timestamp with time zone,
    "end_time" timestamp with time zone,
    "provider" character varying(8),
    "min_5mins" double precision,
    "max_5mins" double precision,
    "order_type" character varying(8),
    "barrier_bound" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'allquotes'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "market" OPTIONS (
    "column_name" 'market'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "mid" OPTIONS (
    "column_name" 'mid'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "activate_id" OPTIONS (
    "column_name" 'activate_id'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "state" OPTIONS (
    "column_name" 'state'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "remains" OPTIONS (
    "column_name" 'remains'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "stop_loss" OPTIONS (
    "column_name" 'stop_loss'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "take_profit" OPTIONS (
    "column_name" 'take_profit'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "parent_id" OPTIONS (
    "column_name" 'parent_id'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "barrier" OPTIONS (
    "column_name" 'barrier'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "max_amount" OPTIONS (
    "column_name" 'max_amount'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "pause" OPTIONS (
    "column_name" 'pause'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "unconfirmed_amount" OPTIONS (
    "column_name" 'unconfirmed_amount'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "amount_pending" OPTIONS (
    "column_name" 'amount_pending'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "start_time" OPTIONS (
    "column_name" 'start_time'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "end_time" OPTIONS (
    "column_name" 'end_time'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "provider" OPTIONS (
    "column_name" 'provider'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "order_type" OPTIONS (
    "column_name" 'order_type'
);
ALTER FOREIGN TABLE "mos"."allquotes" ALTER COLUMN "barrier_bound" OPTIONS (
    "column_name" 'barrier_bound'
);


ALTER FOREIGN TABLE "mos"."allquotes" OWNER TO "postgres";

--
-- TOC entry 284 (class 1259 OID 34945)
-- Name: allquotes_collat; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."allquotes_collat" (
    "code" character varying(16),
    "market" "text",
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "mid" double precision,
    "lot" integer,
    "dlong" double precision,
    "dshort" double precision,
    "money" double precision,
    "long_avail" double precision,
    "short_avail" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'allquotes_collat'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "market" OPTIONS (
    "column_name" 'market'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "mid" OPTIONS (
    "column_name" 'mid'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "dlong" OPTIONS (
    "column_name" 'dlong'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "dshort" OPTIONS (
    "column_name" 'dshort'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "money" OPTIONS (
    "column_name" 'money'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "long_avail" OPTIONS (
    "column_name" 'long_avail'
);
ALTER FOREIGN TABLE "mos"."allquotes_collat" ALTER COLUMN "short_avail" OPTIONS (
    "column_name" 'short_avail'
);


ALTER FOREIGN TABLE "mos"."allquotes_collat" OWNER TO "postgres";

--
-- TOC entry 285 (class 1259 OID 34948)
-- Name: allquotes_mini; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."allquotes_mini" (
    "code" character varying(16),
    "market" "text",
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "mid" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'allquotes_mini'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "market" OPTIONS (
    "column_name" 'market'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."allquotes_mini" ALTER COLUMN "mid" OPTIONS (
    "column_name" 'mid'
);


ALTER FOREIGN TABLE "mos"."allquotes_mini" OWNER TO "postgres";

--
-- TOC entry 286 (class 1259 OID 34951)
-- Name: analytics_beta; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."analytics_beta" (
    "index" bigint,
    "sec" "text",
    "base_asset" "text",
    "beta" double precision,
    "r2" double precision,
    "corr" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'analytics_beta'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "sec" OPTIONS (
    "column_name" 'sec'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "base_asset" OPTIONS (
    "column_name" 'base_asset'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "beta" OPTIONS (
    "column_name" 'beta'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "r2" OPTIONS (
    "column_name" 'r2'
);
ALTER FOREIGN TABLE "mos"."analytics_beta" ALTER COLUMN "corr" OPTIONS (
    "column_name" 'corr'
);


ALTER FOREIGN TABLE "mos"."analytics_beta" OWNER TO "postgres";

--
-- TOC entry 287 (class 1259 OID 34954)
-- Name: analytics_future; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."analytics_future" (
    "index" bigint,
    "ds" timestamp without time zone,
    "yhat_lower" double precision,
    "yhat_upper" double precision,
    "yhat" double precision,
    "sigma" double precision,
    "trend_abs" double precision,
    "trend_rel_pct" double precision,
    "sec" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'analytics_future'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "ds" OPTIONS (
    "column_name" 'ds'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "yhat_lower" OPTIONS (
    "column_name" 'yhat_lower'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "yhat_upper" OPTIONS (
    "column_name" 'yhat_upper'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "yhat" OPTIONS (
    "column_name" 'yhat'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "sigma" OPTIONS (
    "column_name" 'sigma'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "trend_abs" OPTIONS (
    "column_name" 'trend_abs'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "trend_rel_pct" OPTIONS (
    "column_name" 'trend_rel_pct'
);
ALTER FOREIGN TABLE "mos"."analytics_future" ALTER COLUMN "sec" OPTIONS (
    "column_name" 'sec'
);


ALTER FOREIGN TABLE "mos"."analytics_future" OWNER TO "postgres";

--
-- TOC entry 288 (class 1259 OID 34957)
-- Name: analytics_past; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."analytics_past" (
    "index" bigint,
    "additive_terms" double precision,
    "wd" integer,
    "dt" time without time zone,
    "additive_terms_prct" double precision,
    "sec" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'analytics_past'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "additive_terms" OPTIONS (
    "column_name" 'additive_terms'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "wd" OPTIONS (
    "column_name" 'wd'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "dt" OPTIONS (
    "column_name" 'dt'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "additive_terms_prct" OPTIONS (
    "column_name" 'additive_terms_prct'
);
ALTER FOREIGN TABLE "mos"."analytics_past" ALTER COLUMN "sec" OPTIONS (
    "column_name" 'sec'
);


ALTER FOREIGN TABLE "mos"."analytics_past" OWNER TO "postgres";

--
-- TOC entry 289 (class 1259 OID 34960)
-- Name: autoorders; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."autoorders" (
    "TRANS_ID" "text",
    "last_confirmed_id" bigint,
    "unconfirmed_quantity" bigint,
    "ACCOUNT" "text",
    "ACTION" "text",
    "CLASSCODE" "text",
    "SECCODE" "text",
    "OPERATION" "text",
    "PRICE" "text",
    "COMMENT" "text",
    "QUANTITY" "text",
    "in_last_upd" timestamp with time zone,
    "date_time" timestamp without time zone,
    "sent_local_time" timestamp without time zone,
    "time" bigint,
    "trans_id" bigint,
    "status" bigint,
    "result_msg" "text",
    "quantity" double precision,
    "got_local_time" timestamp without time zone,
    "order_num" bigint,
    "gate_reply_time" timestamp without time zone,
    "error_source" bigint,
    "error_code" bigint,
    "ord_trans_id" bigint,
    "order_id" bigint,
    "tradedate" "date",
    "dateopen" "date",
    "timeopen" time without time zone,
    "datecancel" "date",
    "timecancel" time without time zone,
    "orderremains" bigint,
    "orderexecuted" bigint,
    "volume" double precision,
    "state" character varying(16),
    "volumecalc" double precision,
    "cancelreason" "text",
    "execmode" character varying(16)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'autoorders'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "TRANS_ID" OPTIONS (
    "column_name" 'TRANS_ID'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "last_confirmed_id" OPTIONS (
    "column_name" 'last_confirmed_id'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "unconfirmed_quantity" OPTIONS (
    "column_name" 'unconfirmed_quantity'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "ACCOUNT" OPTIONS (
    "column_name" 'ACCOUNT'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "ACTION" OPTIONS (
    "column_name" 'ACTION'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "CLASSCODE" OPTIONS (
    "column_name" 'CLASSCODE'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "SECCODE" OPTIONS (
    "column_name" 'SECCODE'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "OPERATION" OPTIONS (
    "column_name" 'OPERATION'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "PRICE" OPTIONS (
    "column_name" 'PRICE'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "COMMENT" OPTIONS (
    "column_name" 'COMMENT'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "QUANTITY" OPTIONS (
    "column_name" 'QUANTITY'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "in_last_upd" OPTIONS (
    "column_name" 'in_last_upd'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "date_time" OPTIONS (
    "column_name" 'date_time'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "sent_local_time" OPTIONS (
    "column_name" 'sent_local_time'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "trans_id" OPTIONS (
    "column_name" 'trans_id'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "status" OPTIONS (
    "column_name" 'status'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "result_msg" OPTIONS (
    "column_name" 'result_msg'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "got_local_time" OPTIONS (
    "column_name" 'got_local_time'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "order_num" OPTIONS (
    "column_name" 'order_num'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "gate_reply_time" OPTIONS (
    "column_name" 'gate_reply_time'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "error_source" OPTIONS (
    "column_name" 'error_source'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "error_code" OPTIONS (
    "column_name" 'error_code'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "ord_trans_id" OPTIONS (
    "column_name" 'ord_trans_id'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "dateopen" OPTIONS (
    "column_name" 'dateopen'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "timeopen" OPTIONS (
    "column_name" 'timeopen'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "datecancel" OPTIONS (
    "column_name" 'datecancel'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "timecancel" OPTIONS (
    "column_name" 'timecancel'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "orderremains" OPTIONS (
    "column_name" 'orderremains'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "orderexecuted" OPTIONS (
    "column_name" 'orderexecuted'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "state" OPTIONS (
    "column_name" 'state'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "volumecalc" OPTIONS (
    "column_name" 'volumecalc'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "cancelreason" OPTIONS (
    "column_name" 'cancelreason'
);
ALTER FOREIGN TABLE "mos"."autoorders" ALTER COLUMN "execmode" OPTIONS (
    "column_name" 'execmode'
);


ALTER FOREIGN TABLE "mos"."autoorders" OWNER TO "postgres";

--
-- TOC entry 290 (class 1259 OID 34963)
-- Name: autoorders_grouped; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."autoorders_grouped" (
    "code" "text",
    "comment" "text",
    "amount" bigint,
    "unconfirmed_amount" bigint,
    "amount_pending" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'autoorders_grouped'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped" ALTER COLUMN "unconfirmed_amount" OPTIONS (
    "column_name" 'unconfirmed_amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped" ALTER COLUMN "amount_pending" OPTIONS (
    "column_name" 'amount_pending'
);


ALTER FOREIGN TABLE "mos"."autoorders_grouped" OWNER TO "postgres";

--
-- TOC entry 291 (class 1259 OID 34966)
-- Name: autoorders_grouped_tcs; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."autoorders_grouped_tcs" (
    "code" "text",
    "comment" "text",
    "amount" numeric,
    "unconfirmed_amount" numeric,
    "amount_pending" numeric
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'autoorders_grouped_tcs'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" ALTER COLUMN "unconfirmed_amount" OPTIONS (
    "column_name" 'unconfirmed_amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" ALTER COLUMN "amount_pending" OPTIONS (
    "column_name" 'amount_pending'
);


ALTER FOREIGN TABLE "mos"."autoorders_grouped_tcs" OWNER TO "postgres";

--
-- TOC entry 292 (class 1259 OID 34969)
-- Name: autoorders_tcs; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."autoorders_tcs" (
    "quantity" bigint,
    "direction" bigint,
    "account_id" "text",
    "order_type" bigint,
    "order_id" "text",
    "instrument_id" "text",
    "last_upd" timestamp without time zone,
    "comment" "text",
    "code" "text",
    "order_id_out" "text",
    "execution_report_status" bigint,
    "lots_requested" bigint,
    "lots_executed" bigint,
    "unconfirmed_amount" bigint,
    "message" "text",
    "initial_order_price" "text",
    "executed_order_price" "text",
    "total_order_amount" "text",
    "initial_commission" "text",
    "executed_commission" "text",
    "initial_security_price" "text",
    "initial_order_price_pt" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'autoorders_tcs'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "account_id" OPTIONS (
    "column_name" 'account_id'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "order_type" OPTIONS (
    "column_name" 'order_type'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "instrument_id" OPTIONS (
    "column_name" 'instrument_id'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "order_id_out" OPTIONS (
    "column_name" 'order_id_out'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "execution_report_status" OPTIONS (
    "column_name" 'execution_report_status'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "lots_requested" OPTIONS (
    "column_name" 'lots_requested'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "lots_executed" OPTIONS (
    "column_name" 'lots_executed'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "unconfirmed_amount" OPTIONS (
    "column_name" 'unconfirmed_amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "message" OPTIONS (
    "column_name" 'message'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "initial_order_price" OPTIONS (
    "column_name" 'initial_order_price'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "executed_order_price" OPTIONS (
    "column_name" 'executed_order_price'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "total_order_amount" OPTIONS (
    "column_name" 'total_order_amount'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "initial_commission" OPTIONS (
    "column_name" 'initial_commission'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "executed_commission" OPTIONS (
    "column_name" 'executed_commission'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "initial_security_price" OPTIONS (
    "column_name" 'initial_security_price'
);
ALTER FOREIGN TABLE "mos"."autoorders_tcs" ALTER COLUMN "initial_order_price_pt" OPTIONS (
    "column_name" 'initial_order_price_pt'
);


ALTER FOREIGN TABLE "mos"."autoorders_tcs" OWNER TO "postgres";

--
-- TOC entry 293 (class 1259 OID 34972)
-- Name: deals; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals" (
    "deal_id" bigint NOT NULL,
    "order_id" bigint NOT NULL,
    "time" time without time zone,
    "bs" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "comment" character varying(64),
    "broker_fees" double precision,
    "tradedate" "date" NOT NULL,
    "class_code" character varying(32)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "deal_id" OPTIONS (
    "column_name" 'deal_id'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "bs" OPTIONS (
    "column_name" 'bs'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "broker_fees" OPTIONS (
    "column_name" 'broker_fees'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."deals" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);


ALTER FOREIGN TABLE "mos"."deals" OWNER TO "postgres";

--
-- TOC entry 294 (class 1259 OID 34975)
-- Name: deals_ba; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_ba" (
    "code" character varying(16),
    "bid" bigint,
    "price" double precision,
    "ask" bigint,
    "updated_at" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_ba'
);
ALTER FOREIGN TABLE "mos"."deals_ba" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_ba" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."deals_ba" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_ba" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."deals_ba" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);


ALTER FOREIGN TABLE "mos"."deals_ba" OWNER TO "postgres";

--
-- TOC entry 295 (class 1259 OID 34978)
-- Name: deals_ba_hist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_ba_hist" (
    "code" character varying(16) NOT NULL,
    "price" double precision NOT NULL,
    "last_upd" timestamp with time zone NOT NULL,
    "bid" bigint,
    "ask" bigint,
    "updated_at" timestamp with time zone,
    "bidt1" bigint,
    "askt1" bigint,
    "updated_at_t1" timestamp with time zone,
    "dbid" bigint,
    "dask" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_ba_hist'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "bidt1" OPTIONS (
    "column_name" 'bidt1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "askt1" OPTIONS (
    "column_name" 'askt1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "updated_at_t1" OPTIONS (
    "column_name" 'updated_at_t1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "dbid" OPTIONS (
    "column_name" 'dbid'
);
ALTER FOREIGN TABLE "mos"."deals_ba_hist" ALTER COLUMN "dask" OPTIONS (
    "column_name" 'dask'
);


ALTER FOREIGN TABLE "mos"."deals_ba_hist" OWNER TO "postgres";

--
-- TOC entry 296 (class 1259 OID 34981)
-- Name: deals_ba_t1; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_ba_t1" (
    "code" character varying(16),
    "bid" bigint,
    "price" double precision,
    "ask" bigint,
    "updated_at" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_ba_t1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_t1" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_ba_t1" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."deals_ba_t1" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_ba_t1" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."deals_ba_t1" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);


ALTER FOREIGN TABLE "mos"."deals_ba_t1" OWNER TO "postgres";

--
-- TOC entry 297 (class 1259 OID 34984)
-- Name: deals_ba_view; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_ba_view" (
    "code" character varying(16),
    "price" double precision,
    "last_upd" timestamp with time zone,
    "bid" bigint,
    "ask" bigint,
    "updated_at" timestamp with time zone,
    "bidt1" bigint,
    "askt1" bigint,
    "updated_at_t1" timestamp with time zone,
    "dbid" bigint,
    "dask" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_ba_view'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "bidt1" OPTIONS (
    "column_name" 'bidt1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "askt1" OPTIONS (
    "column_name" 'askt1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "updated_at_t1" OPTIONS (
    "column_name" 'updated_at_t1'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "dbid" OPTIONS (
    "column_name" 'dbid'
);
ALTER FOREIGN TABLE "mos"."deals_ba_view" ALTER COLUMN "dask" OPTIONS (
    "column_name" 'dask'
);


ALTER FOREIGN TABLE "mos"."deals_ba_view" OWNER TO "postgres";

--
-- TOC entry 298 (class 1259 OID 34987)
-- Name: deals_imp; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_imp" (
    "deal_id" numeric(20,0) NOT NULL,
    "tradedate" "date" NOT NULL,
    "time" time without time zone,
    "time_msc" integer,
    "period" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "bs" character varying(16),
    "open_interest" integer
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_imp'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "deal_id" OPTIONS (
    "column_name" 'deal_id'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "time_msc" OPTIONS (
    "column_name" 'time_msc'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "period" OPTIONS (
    "column_name" 'period'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "bs" OPTIONS (
    "column_name" 'bs'
);
ALTER FOREIGN TABLE "mos"."deals_imp" ALTER COLUMN "open_interest" OPTIONS (
    "column_name" 'open_interest'
);


ALTER FOREIGN TABLE "mos"."deals_imp" OWNER TO "postgres";

--
-- TOC entry 299 (class 1259 OID 34990)
-- Name: deals_imp_arch; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_imp_arch" (
    "deal_id" numeric(20,0) NOT NULL,
    "tradedate" "date" NOT NULL,
    "time" time without time zone,
    "time_msc" integer,
    "period" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "bs" character varying(16),
    "open_interest" integer
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_imp_arch'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "deal_id" OPTIONS (
    "column_name" 'deal_id'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "time_msc" OPTIONS (
    "column_name" 'time_msc'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "period" OPTIONS (
    "column_name" 'period'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "bs" OPTIONS (
    "column_name" 'bs'
);
ALTER FOREIGN TABLE "mos"."deals_imp_arch" ALTER COLUMN "open_interest" OPTIONS (
    "column_name" 'open_interest'
);


ALTER FOREIGN TABLE "mos"."deals_imp_arch" OWNER TO "postgres";

--
-- TOC entry 300 (class 1259 OID 34993)
-- Name: deals_myhist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deals_myhist" (
    "deal_id" bigint NOT NULL,
    "order_id" bigint,
    "time" time without time zone,
    "bs" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "comment" character varying(64),
    "broker_fees" double precision,
    "tradedate" "date" NOT NULL,
    "class_code" character varying(32)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deals_myhist'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "deal_id" OPTIONS (
    "column_name" 'deal_id'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "bs" OPTIONS (
    "column_name" 'bs'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "broker_fees" OPTIONS (
    "column_name" 'broker_fees'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."deals_myhist" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);


ALTER FOREIGN TABLE "mos"."deals_myhist" OWNER TO "postgres";

--
-- TOC entry 301 (class 1259 OID 34996)
-- Name: deorders; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."deorders" (
    "order_id" bigint,
    "tradedate" "date",
    "dateopen" "date",
    "timeopen" time without time zone,
    "datecancel" "date",
    "timecancel" time without time zone,
    "code" character varying(32),
    "instrument" character varying(32),
    "bs" character varying(16),
    "price" double precision,
    "orderamount" bigint,
    "orderremains" bigint,
    "orderexecuted" bigint,
    "volume" double precision,
    "comment" character varying(32),
    "type" character varying(16),
    "state" character varying(16),
    "volumecalc" double precision,
    "class_code" character varying(16),
    "cancelreason" "text",
    "execmode" character varying(16),
    "mcsopen" bigint,
    "mcscancel" bigint,
    "trans_id" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'deorders'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "dateopen" OPTIONS (
    "column_name" 'dateopen'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "timeopen" OPTIONS (
    "column_name" 'timeopen'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "datecancel" OPTIONS (
    "column_name" 'datecancel'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "timecancel" OPTIONS (
    "column_name" 'timecancel'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "instrument" OPTIONS (
    "column_name" 'instrument'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "bs" OPTIONS (
    "column_name" 'bs'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "orderamount" OPTIONS (
    "column_name" 'orderamount'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "orderremains" OPTIONS (
    "column_name" 'orderremains'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "orderexecuted" OPTIONS (
    "column_name" 'orderexecuted'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "state" OPTIONS (
    "column_name" 'state'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "volumecalc" OPTIONS (
    "column_name" 'volumecalc'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "cancelreason" OPTIONS (
    "column_name" 'cancelreason'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "execmode" OPTIONS (
    "column_name" 'execmode'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "mcsopen" OPTIONS (
    "column_name" 'mcsopen'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "mcscancel" OPTIONS (
    "column_name" 'mcscancel'
);
ALTER FOREIGN TABLE "mos"."deorders" ALTER COLUMN "trans_id" OPTIONS (
    "column_name" 'trans_id'
);


ALTER FOREIGN TABLE "mos"."deorders" OWNER TO "postgres";

--
-- TOC entry 302 (class 1259 OID 34999)
-- Name: df_all_candles_t; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_candles_t" (
    "open" double precision NOT NULL,
    "high" double precision NOT NULL,
    "low" double precision NOT NULL,
    "close" double precision NOT NULL,
    "volume" integer NOT NULL,
    "security" character varying(64) NOT NULL,
    "class_code" character varying(64),
    "datetime" timestamp with time zone NOT NULL
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_candles_t'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "open" OPTIONS (
    "column_name" 'open'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "high" OPTIONS (
    "column_name" 'high'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "low" OPTIONS (
    "column_name" 'low'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "close" OPTIONS (
    "column_name" 'close'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);


ALTER FOREIGN TABLE "mos"."df_all_candles_t" OWNER TO "postgres";

--
-- TOC entry 303 (class 1259 OID 35002)
-- Name: df_all_candles_t_arch; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_candles_t_arch" (
    "open" double precision NOT NULL,
    "high" double precision NOT NULL,
    "low" double precision NOT NULL,
    "close" double precision NOT NULL,
    "volume" integer NOT NULL,
    "security" character varying(64) NOT NULL,
    "class_code" character varying(64),
    "datetime" timestamp with time zone NOT NULL
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_candles_t_arch'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "open" OPTIONS (
    "column_name" 'open'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "high" OPTIONS (
    "column_name" 'high'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "low" OPTIONS (
    "column_name" 'low'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "close" OPTIONS (
    "column_name" 'close'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);


ALTER FOREIGN TABLE "mos"."df_all_candles_t_arch" OWNER TO "postgres";

--
-- TOC entry 304 (class 1259 OID 35005)
-- Name: df_all_levels; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_levels" (
    "index" bigint,
    "code" "text",
    "name" "text",
    "start" double precision,
    "end" double precision,
    "logic" bigint,
    "std" double precision,
    "timestamp" timestamp without time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_levels'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "name" OPTIONS (
    "column_name" 'name'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "start" OPTIONS (
    "column_name" 'start'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "end" OPTIONS (
    "column_name" 'end'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "logic" OPTIONS (
    "column_name" 'logic'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."df_all_levels" ALTER COLUMN "timestamp" OPTIONS (
    "column_name" 'timestamp'
);


ALTER FOREIGN TABLE "mos"."df_all_levels" OWNER TO "postgres";

--
-- TOC entry 305 (class 1259 OID 35008)
-- Name: df_all_orderbook_arch; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_orderbook_arch" (
    "price" "text",
    "quantity" bigint,
    "ba" "text",
    "datetime" timestamp with time zone,
    "code" "text",
    "abnormal" boolean,
    "limit" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_orderbook_arch'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "ba" OPTIONS (
    "column_name" 'ba'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "abnormal" OPTIONS (
    "column_name" 'abnormal'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" ALTER COLUMN "limit" OPTIONS (
    "column_name" 'limit'
);


ALTER FOREIGN TABLE "mos"."df_all_orderbook_arch" OWNER TO "postgres";

--
-- TOC entry 306 (class 1259 OID 35011)
-- Name: df_all_orderbook_t; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_orderbook_t" (
    "price" "text",
    "quantity" bigint,
    "ba" "text",
    "datetime" timestamp with time zone,
    "code" "text",
    "abnormal" boolean,
    "limit" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_orderbook_t'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "ba" OPTIONS (
    "column_name" 'ba'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "abnormal" OPTIONS (
    "column_name" 'abnormal'
);
ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" ALTER COLUMN "limit" OPTIONS (
    "column_name" 'limit'
);


ALTER FOREIGN TABLE "mos"."df_all_orderbook_t" OWNER TO "postgres";

--
-- TOC entry 307 (class 1259 OID 35014)
-- Name: df_all_volumes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_all_volumes" (
    "index" bigint,
    "price" double precision,
    "volume" double precision,
    "code" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_all_volumes'
);
ALTER FOREIGN TABLE "mos"."df_all_volumes" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."df_all_volumes" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."df_all_volumes" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."df_all_volumes" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);


ALTER FOREIGN TABLE "mos"."df_all_volumes" OWNER TO "postgres";

--
-- TOC entry 308 (class 1259 OID 35017)
-- Name: df_bollinger; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_bollinger" (
    "index" bigint,
    "security" "text",
    "class_code" "text",
    "mean" double precision,
    "std" double precision,
    "count" bigint,
    "prct" double precision,
    "up" double precision,
    "down" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_bollinger'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "prct" OPTIONS (
    "column_name" 'prct'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "up" OPTIONS (
    "column_name" 'up'
);
ALTER FOREIGN TABLE "mos"."df_bollinger" ALTER COLUMN "down" OPTIONS (
    "column_name" 'down'
);


ALTER FOREIGN TABLE "mos"."df_bollinger" OWNER TO "postgres";

--
-- TOC entry 309 (class 1259 OID 35020)
-- Name: df_levels; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_levels" (
    "index" bigint,
    "price" double precision,
    "volume" double precision,
    "std" double precision,
    "sec" "text",
    "min_start" double precision,
    "max_start" double precision,
    "end" double precision,
    "sl" double precision,
    "mid" double precision,
    "down" "text",
    "prev_end" double precision,
    "next_sl" double precision,
    "implied_prob" double precision,
    "timestamp" timestamp without time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_levels'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "sec" OPTIONS (
    "column_name" 'sec'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "min_start" OPTIONS (
    "column_name" 'min_start'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "max_start" OPTIONS (
    "column_name" 'max_start'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "end" OPTIONS (
    "column_name" 'end'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "sl" OPTIONS (
    "column_name" 'sl'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "mid" OPTIONS (
    "column_name" 'mid'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "down" OPTIONS (
    "column_name" 'down'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "prev_end" OPTIONS (
    "column_name" 'prev_end'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "next_sl" OPTIONS (
    "column_name" 'next_sl'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "implied_prob" OPTIONS (
    "column_name" 'implied_prob'
);
ALTER FOREIGN TABLE "mos"."df_levels" ALTER COLUMN "timestamp" OPTIONS (
    "column_name" 'timestamp'
);


ALTER FOREIGN TABLE "mos"."df_levels" OWNER TO "postgres";

--
-- TOC entry 310 (class 1259 OID 35023)
-- Name: df_monitor; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_monitor" (
    "index" bigint,
    "code" "text",
    "old_state" "text",
    "old_price" double precision,
    "old_start" double precision,
    "old_end" double precision,
    "new_state" "text",
    "new_price" double precision,
    "new_start" double precision,
    "new_end" double precision,
    "std" double precision,
    "old_timestamp" timestamp with time zone,
    "new_timestamp" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_monitor'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "old_state" OPTIONS (
    "column_name" 'old_state'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "old_price" OPTIONS (
    "column_name" 'old_price'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "old_start" OPTIONS (
    "column_name" 'old_start'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "old_end" OPTIONS (
    "column_name" 'old_end'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "new_state" OPTIONS (
    "column_name" 'new_state'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "new_price" OPTIONS (
    "column_name" 'new_price'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "new_start" OPTIONS (
    "column_name" 'new_start'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "new_end" OPTIONS (
    "column_name" 'new_end'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "old_timestamp" OPTIONS (
    "column_name" 'old_timestamp'
);
ALTER FOREIGN TABLE "mos"."df_monitor" ALTER COLUMN "new_timestamp" OPTIONS (
    "column_name" 'new_timestamp'
);


ALTER FOREIGN TABLE "mos"."df_monitor" OWNER TO "postgres";

--
-- TOC entry 311 (class 1259 OID 35026)
-- Name: df_volumes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."df_volumes" (
    "security" character varying(64),
    "class_code" character varying(64),
    "tm" timestamp without time zone,
    "points_num" bigint,
    "volume_std" numeric,
    "volume_std_10" numeric,
    "volume_avg" bigint,
    "volume_avg_10" numeric,
    "money_volume_avg" double precision,
    "money_volume_avg_10" double precision,
    "diff_mean" double precision,
    "diff_mean_10" double precision,
    "diff_std" double precision,
    "diff_std_10" double precision,
    "diff_prct_mean" double precision,
    "diff_prct_mean_10" double precision,
    "diff_prct_std" double precision,
    "diff_prct_std_10" double precision,
    "cnt_days" bigint,
    "max_dt" "date",
    "max_datetime" timestamp with time zone,
    "close" double precision,
    "volume_last" integer,
    "money_volume_last" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'df_volumes'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "tm" OPTIONS (
    "column_name" 'tm'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "points_num" OPTIONS (
    "column_name" 'points_num'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "volume_std" OPTIONS (
    "column_name" 'volume_std'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "volume_std_10" OPTIONS (
    "column_name" 'volume_std_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "volume_avg" OPTIONS (
    "column_name" 'volume_avg'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "volume_avg_10" OPTIONS (
    "column_name" 'volume_avg_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "money_volume_avg" OPTIONS (
    "column_name" 'money_volume_avg'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "money_volume_avg_10" OPTIONS (
    "column_name" 'money_volume_avg_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_mean" OPTIONS (
    "column_name" 'diff_mean'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_mean_10" OPTIONS (
    "column_name" 'diff_mean_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_std" OPTIONS (
    "column_name" 'diff_std'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_std_10" OPTIONS (
    "column_name" 'diff_std_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_prct_mean" OPTIONS (
    "column_name" 'diff_prct_mean'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_prct_mean_10" OPTIONS (
    "column_name" 'diff_prct_mean_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_prct_std" OPTIONS (
    "column_name" 'diff_prct_std'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "diff_prct_std_10" OPTIONS (
    "column_name" 'diff_prct_std_10'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "cnt_days" OPTIONS (
    "column_name" 'cnt_days'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "max_dt" OPTIONS (
    "column_name" 'max_dt'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "close" OPTIONS (
    "column_name" 'close'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "volume_last" OPTIONS (
    "column_name" 'volume_last'
);
ALTER FOREIGN TABLE "mos"."df_volumes" ALTER COLUMN "money_volume_last" OPTIONS (
    "column_name" 'money_volume_last'
);


ALTER FOREIGN TABLE "mos"."df_volumes" OWNER TO "postgres";

--
-- TOC entry 312 (class 1259 OID 35029)
-- Name: diffhist_t1510; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhist_t1510" (
    "index" bigint,
    "code" "text",
    "board" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhist_t1510'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "min_datetime" OPTIONS (
    "column_name" 'min_datetime'
);
ALTER FOREIGN TABLE "mos"."diffhist_t1510" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);


ALTER FOREIGN TABLE "mos"."diffhist_t1510" OWNER TO "postgres";

--
-- TOC entry 313 (class 1259 OID 35032)
-- Name: diffhist_t5; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhist_t5" (
    "index" bigint,
    "code" "text",
    "board" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhist_t5'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "min_datetime" OPTIONS (
    "column_name" 'min_datetime'
);
ALTER FOREIGN TABLE "mos"."diffhist_t5" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);


ALTER FOREIGN TABLE "mos"."diffhist_t5" OWNER TO "postgres";

--
-- TOC entry 314 (class 1259 OID 35035)
-- Name: diffhistview; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhistview" (
    "code" character varying(16),
    "board" "text",
    "min" double precision,
    "max" double precision,
    "volume" double precision,
    "count" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhistview'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhistview" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);


ALTER FOREIGN TABLE "mos"."diffhistview" OWNER TO "postgres";

--
-- TOC entry 315 (class 1259 OID 35038)
-- Name: diffhistview_5; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhistview_5" (
    "code" character varying(16),
    "board" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" double precision,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhistview_5'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "min_datetime" OPTIONS (
    "column_name" 'min_datetime'
);
ALTER FOREIGN TABLE "mos"."diffhistview_5" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);


ALTER FOREIGN TABLE "mos"."diffhistview_5" OWNER TO "postgres";

--
-- TOC entry 316 (class 1259 OID 35041)
-- Name: diffhistview_t1510; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhistview_t1510" (
    "code" character varying(64),
    "board" character varying(64),
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhistview_t1510'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "min_datetime" OPTIONS (
    "column_name" 'min_datetime'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t1510" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);


ALTER FOREIGN TABLE "mos"."diffhistview_t1510" OWNER TO "postgres";

--
-- TOC entry 317 (class 1259 OID 35044)
-- Name: diffhistview_t5; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffhistview_t5" (
    "code" character varying(64),
    "board" character varying(64),
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffhistview_t5'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "min_datetime" OPTIONS (
    "column_name" 'min_datetime'
);
ALTER FOREIGN TABLE "mos"."diffhistview_t5" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);


ALTER FOREIGN TABLE "mos"."diffhistview_t5" OWNER TO "postgres";

--
-- TOC entry 318 (class 1259 OID 35047)
-- Name: diffminmax; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."diffminmax" (
    "code" "text",
    "board" "text",
    "min_5mins" double precision,
    "max_5mins" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'diffminmax'
);
ALTER FOREIGN TABLE "mos"."diffminmax" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."diffminmax" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."diffminmax" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."diffminmax" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);


ALTER FOREIGN TABLE "mos"."diffminmax" OWNER TO "postgres";

--
-- TOC entry 319 (class 1259 OID 35050)
-- Name: event_news; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."event_news" (
    "code" character varying(32) NOT NULL,
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(32) NOT NULL,
    "news_time" timestamp with time zone NOT NULL,
    "keyword" character varying(32),
    "msg" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'event_news'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "date_discovery" OPTIONS (
    "column_name" 'date_discovery'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "channel_source" OPTIONS (
    "column_name" 'channel_source'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "news_time" OPTIONS (
    "column_name" 'news_time'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "keyword" OPTIONS (
    "column_name" 'keyword'
);
ALTER FOREIGN TABLE "mos"."event_news" ALTER COLUMN "msg" OPTIONS (
    "column_name" 'msg'
);


ALTER FOREIGN TABLE "mos"."event_news" OWNER TO "postgres";

--
-- TOC entry 320 (class 1259 OID 35053)
-- Name: events_jumps_hist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."events_jumps_hist" (
    "index" bigint,
    "code" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "process_time" timestamp with time zone,
    "jump_prct" double precision,
    "out_prct" double precision,
    "volume_peak" double precision,
    "out_std" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'events_jumps_hist'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "process_time" OPTIONS (
    "column_name" 'process_time'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "jump_prct" OPTIONS (
    "column_name" 'jump_prct'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "out_prct" OPTIONS (
    "column_name" 'out_prct'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "volume_peak" OPTIONS (
    "column_name" 'volume_peak'
);
ALTER FOREIGN TABLE "mos"."events_jumps_hist" ALTER COLUMN "out_std" OPTIONS (
    "column_name" 'out_std'
);


ALTER FOREIGN TABLE "mos"."events_jumps_hist" OWNER TO "postgres";

--
-- TOC entry 321 (class 1259 OID 35056)
-- Name: futprefix; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."futprefix" (
    "ticker" character varying(8) NOT NULL,
    "futprefix" character varying(4)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'futprefix'
);
ALTER FOREIGN TABLE "mos"."futprefix" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."futprefix" ALTER COLUMN "futprefix" OPTIONS (
    "column_name" 'futprefix'
);


ALTER FOREIGN TABLE "mos"."futprefix" OWNER TO "postgres";

--
-- TOC entry 322 (class 1259 OID 35059)
-- Name: futquotes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."futquotes" (
    "fullid" character varying(128),
    "code" character varying(16),
    "status" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "collateral" double precision,
    "minprice" double precision,
    "maxprice" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "tillmaturity" integer,
    "maturitydate" character varying(16),
    "tradedate" character varying(12),
    "closeprice" double precision,
    "prctchange" double precision,
    "instrumentid" character varying(32),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "pricestepcur" double precision,
    "updated_at" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'futquotes'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "fullid" OPTIONS (
    "column_name" 'fullid'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "status" OPTIONS (
    "column_name" 'status'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "collateral" OPTIONS (
    "column_name" 'collateral'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "minprice" OPTIONS (
    "column_name" 'minprice'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "maxprice" OPTIONS (
    "column_name" 'maxprice'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "openinterest" OPTIONS (
    "column_name" 'openinterest'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "tillmaturity" OPTIONS (
    "column_name" 'tillmaturity'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "maturitydate" OPTIONS (
    "column_name" 'maturitydate'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "closeprice" OPTIONS (
    "column_name" 'closeprice'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "prctchange" OPTIONS (
    "column_name" 'prctchange'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "instrumentid" OPTIONS (
    "column_name" 'instrumentid'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "prec" OPTIONS (
    "column_name" 'prec'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "pricestep" OPTIONS (
    "column_name" 'pricestep'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "lastdealqty" OPTIONS (
    "column_name" 'lastdealqty'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "lastdealvol" OPTIONS (
    "column_name" 'lastdealvol'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "pricestepcur" OPTIONS (
    "column_name" 'pricestepcur'
);
ALTER FOREIGN TABLE "mos"."futquotes" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);


ALTER FOREIGN TABLE "mos"."futquotes" OWNER TO "postgres";

--
-- TOC entry 323 (class 1259 OID 35062)
-- Name: futquotesdiff; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."futquotesdiff" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'futquotesdiff'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "openinterest" OPTIONS (
    "column_name" 'openinterest'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."futquotesdiff" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);


ALTER FOREIGN TABLE "mos"."futquotesdiff" OWNER TO "postgres";

--
-- TOC entry 324 (class 1259 OID 35065)
-- Name: futquotesdiffhist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."futquotesdiffhist" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'futquotesdiffhist'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "openinterest" OPTIONS (
    "column_name" 'openinterest'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."futquotesdiffhist" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);


ALTER FOREIGN TABLE "mos"."futquotesdiffhist" OWNER TO "postgres";

--
-- TOC entry 325 (class 1259 OID 35068)
-- Name: futquoteshist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."futquoteshist" (
    "fullid" character varying(128),
    "code" character varying(16),
    "status" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "collateral" double precision,
    "minprice" double precision,
    "maxprice" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "tillmaturity" integer,
    "maturitydate" character varying(16),
    "tradedate" character varying(12),
    "closeprice" double precision,
    "prctchange" double precision,
    "instrumentid" character varying(32),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "pricestepcur" double precision,
    "updated_at" timestamp with time zone,
    "snaptimestamp" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'futquoteshist'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "fullid" OPTIONS (
    "column_name" 'fullid'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "status" OPTIONS (
    "column_name" 'status'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "collateral" OPTIONS (
    "column_name" 'collateral'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "minprice" OPTIONS (
    "column_name" 'minprice'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "maxprice" OPTIONS (
    "column_name" 'maxprice'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "openinterest" OPTIONS (
    "column_name" 'openinterest'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "tillmaturity" OPTIONS (
    "column_name" 'tillmaturity'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "maturitydate" OPTIONS (
    "column_name" 'maturitydate'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "closeprice" OPTIONS (
    "column_name" 'closeprice'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "prctchange" OPTIONS (
    "column_name" 'prctchange'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "instrumentid" OPTIONS (
    "column_name" 'instrumentid'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "prec" OPTIONS (
    "column_name" 'prec'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "pricestep" OPTIONS (
    "column_name" 'pricestep'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "lastdealqty" OPTIONS (
    "column_name" 'lastdealqty'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "lastdealvol" OPTIONS (
    "column_name" 'lastdealvol'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "pricestepcur" OPTIONS (
    "column_name" 'pricestepcur'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."futquoteshist" ALTER COLUMN "snaptimestamp" OPTIONS (
    "column_name" 'snaptimestamp'
);


ALTER FOREIGN TABLE "mos"."futquoteshist" OWNER TO "postgres";

--
-- TOC entry 326 (class 1259 OID 35071)
-- Name: jump_events; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."jump_events" (
    "code" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "process_time" timestamp with time zone,
    "jump_prct" double precision,
    "out_prct" double precision,
    "volume_peak" double precision,
    "out_std" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'jump_events'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "mean" OPTIONS (
    "column_name" 'mean'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "process_time" OPTIONS (
    "column_name" 'process_time'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "jump_prct" OPTIONS (
    "column_name" 'jump_prct'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "out_prct" OPTIONS (
    "column_name" 'out_prct'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "volume_peak" OPTIONS (
    "column_name" 'volume_peak'
);
ALTER FOREIGN TABLE "mos"."jump_events" ALTER COLUMN "out_std" OPTIONS (
    "column_name" 'out_std'
);


ALTER FOREIGN TABLE "mos"."jump_events" OWNER TO "postgres";

--
-- TOC entry 327 (class 1259 OID 35074)
-- Name: money; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."money" (
    "board" character varying,
    "money" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'money'
);
ALTER FOREIGN TABLE "mos"."money" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."money" ALTER COLUMN "money" OPTIONS (
    "column_name" 'money'
);


ALTER FOREIGN TABLE "mos"."money" OWNER TO "postgres";

--
-- TOC entry 328 (class 1259 OID 35077)
-- Name: news_tfidf; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."news_tfidf" (
    "ticker" "text",
    "tfidfsum" double precision,
    "total_daily" bigint,
    "total_with_ticker" bigint,
    "date" "date"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'news_tfidf'
);
ALTER FOREIGN TABLE "mos"."news_tfidf" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."news_tfidf" ALTER COLUMN "tfidfsum" OPTIONS (
    "column_name" 'tfidfsum'
);
ALTER FOREIGN TABLE "mos"."news_tfidf" ALTER COLUMN "total_daily" OPTIONS (
    "column_name" 'total_daily'
);
ALTER FOREIGN TABLE "mos"."news_tfidf" ALTER COLUMN "total_with_ticker" OPTIONS (
    "column_name" 'total_with_ticker'
);
ALTER FOREIGN TABLE "mos"."news_tfidf" ALTER COLUMN "date" OPTIONS (
    "column_name" 'date'
);


ALTER FOREIGN TABLE "mos"."news_tfidf" OWNER TO "postgres";

--
-- TOC entry 329 (class 1259 OID 35080)
-- Name: order_discovery; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."order_discovery" (
    "code" character varying(32),
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(32),
    "news_time" timestamp with time zone,
    "min_val" double precision,
    "max_val" double precision,
    "mean_val" double precision,
    "volume" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'order_discovery'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "date_discovery" OPTIONS (
    "column_name" 'date_discovery'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "channel_source" OPTIONS (
    "column_name" 'channel_source'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "news_time" OPTIONS (
    "column_name" 'news_time'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "min_val" OPTIONS (
    "column_name" 'min_val'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "max_val" OPTIONS (
    "column_name" 'max_val'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "mean_val" OPTIONS (
    "column_name" 'mean_val'
);
ALTER FOREIGN TABLE "mos"."order_discovery" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);


ALTER FOREIGN TABLE "mos"."order_discovery" OWNER TO "postgres";

--
-- TOC entry 330 (class 1259 OID 35083)
-- Name: order_dividend; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."order_dividend" (
    "ticker" character varying(16) NOT NULL,
    "divval_gte" double precision,
    "gte_order_id" bigint,
    "divval_lte" double precision,
    "lte_order_id" bigint,
    "is_activated" boolean,
    "activation_time" timestamp without time zone,
    "dividend" character varying(32)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'order_dividend'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "divval_gte" OPTIONS (
    "column_name" 'divval_gte'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "gte_order_id" OPTIONS (
    "column_name" 'gte_order_id'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "divval_lte" OPTIONS (
    "column_name" 'divval_lte'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "lte_order_id" OPTIONS (
    "column_name" 'lte_order_id'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "is_activated" OPTIONS (
    "column_name" 'is_activated'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "activation_time" OPTIONS (
    "column_name" 'activation_time'
);
ALTER FOREIGN TABLE "mos"."order_dividend" ALTER COLUMN "dividend" OPTIONS (
    "column_name" 'dividend'
);


ALTER FOREIGN TABLE "mos"."order_dividend" OWNER TO "postgres";

--
-- TOC entry 331 (class 1259 OID 35086)
-- Name: orders_auto; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_auto" (
    "code" character varying(16),
    "market" character varying(16),
    "amount" bigint,
    "limit" double precision,
    "executed" bigint,
    "lastorder" bigint,
    "maxspreadprc" double precision,
    "id" integer NOT NULL,
    "strategy" character varying(16)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_auto'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "market" OPTIONS (
    "column_name" 'market'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "limit" OPTIONS (
    "column_name" 'limit'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "executed" OPTIONS (
    "column_name" 'executed'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "lastorder" OPTIONS (
    "column_name" 'lastorder'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "maxspreadprc" OPTIONS (
    "column_name" 'maxspreadprc'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_auto" ALTER COLUMN "strategy" OPTIONS (
    "column_name" 'strategy'
);


ALTER FOREIGN TABLE "mos"."orders_auto" OWNER TO "postgres";

--
-- TOC entry 332 (class 1259 OID 35089)
-- Name: orders_event_activator; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_event_activator" (
    "id" bigint NOT NULL,
    "jumps_id" bigint,
    "news_id" bigint,
    "price_id" bigint,
    "is_activated" boolean NOT NULL,
    "activation_time" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_event_activator'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "jumps_id" OPTIONS (
    "column_name" 'jumps_id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "news_id" OPTIONS (
    "column_name" 'news_id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "price_id" OPTIONS (
    "column_name" 'price_id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "is_activated" OPTIONS (
    "column_name" 'is_activated'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator" ALTER COLUMN "activation_time" OPTIONS (
    "column_name" 'activation_time'
);


ALTER FOREIGN TABLE "mos"."orders_event_activator" OWNER TO "postgres";

--
-- TOC entry 333 (class 1259 OID 35092)
-- Name: orders_event_activator_jumps; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_event_activator_jumps" (
    "id" bigint NOT NULL,
    "ticker" character varying(16) NOT NULL,
    "start_date" timestamp with time zone NOT NULL,
    "end_date" timestamp with time zone NOT NULL,
    "is_activated" boolean NOT NULL,
    "orders_my_id" integer NOT NULL,
    "jump_prct" double precision,
    "out_prct" double precision,
    "volume_peak" double precision,
    "out_std" double precision,
    "activate_time" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_event_activator_jumps'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "start_date" OPTIONS (
    "column_name" 'start_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "end_date" OPTIONS (
    "column_name" 'end_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "is_activated" OPTIONS (
    "column_name" 'is_activated'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "orders_my_id" OPTIONS (
    "column_name" 'orders_my_id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "jump_prct" OPTIONS (
    "column_name" 'jump_prct'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "out_prct" OPTIONS (
    "column_name" 'out_prct'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "volume_peak" OPTIONS (
    "column_name" 'volume_peak'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "out_std" OPTIONS (
    "column_name" 'out_std'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" ALTER COLUMN "activate_time" OPTIONS (
    "column_name" 'activate_time'
);


ALTER FOREIGN TABLE "mos"."orders_event_activator_jumps" OWNER TO "postgres";

--
-- TOC entry 334 (class 1259 OID 35095)
-- Name: orders_event_activator_news; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_event_activator_news" (
    "id" bigint NOT NULL,
    "ticker" character varying(16),
    "keyword" character varying(16),
    "start_date" timestamp with time zone,
    "end_date" timestamp with time zone,
    "is_activated" boolean,
    "activate_time" timestamp with time zone,
    "channel_source" character varying(32)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_event_activator_news'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "keyword" OPTIONS (
    "column_name" 'keyword'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "start_date" OPTIONS (
    "column_name" 'start_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "end_date" OPTIONS (
    "column_name" 'end_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "is_activated" OPTIONS (
    "column_name" 'is_activated'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "activate_time" OPTIONS (
    "column_name" 'activate_time'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_news" ALTER COLUMN "channel_source" OPTIONS (
    "column_name" 'channel_source'
);


ALTER FOREIGN TABLE "mos"."orders_event_activator_news" OWNER TO "postgres";

--
-- TOC entry 335 (class 1259 OID 35098)
-- Name: orders_event_activator_price; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_event_activator_price" (
    "id" bigint NOT NULL,
    "ticker" character varying(16) NOT NULL,
    "price_limit" double precision,
    "start_date" timestamp with time zone NOT NULL,
    "end_date" timestamp with time zone NOT NULL,
    "is_activated" boolean NOT NULL,
    "activate_time" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_event_activator_price'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "price_limit" OPTIONS (
    "column_name" 'price_limit'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "start_date" OPTIONS (
    "column_name" 'start_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "end_date" OPTIONS (
    "column_name" 'end_date'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "is_activated" OPTIONS (
    "column_name" 'is_activated'
);
ALTER FOREIGN TABLE "mos"."orders_event_activator_price" ALTER COLUMN "activate_time" OPTIONS (
    "column_name" 'activate_time'
);


ALTER FOREIGN TABLE "mos"."orders_event_activator_price" OWNER TO "postgres";

--
-- TOC entry 336 (class 1259 OID 35101)
-- Name: orders_in; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_in" (
    "index" bigint,
    "TRANS_ID" "text",
    "CLIENT_CODE" "text",
    "ACCOUNT" "text",
    "ACTION" "text",
    "CLASSCODE" "text",
    "SECCODE" "text",
    "OPERATION" "text",
    "PRICE" "text",
    "QUANTITY" "text",
    "COMMENT" "text",
    "TYPE" "text",
    "last_upd" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_in'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "TRANS_ID" OPTIONS (
    "column_name" 'TRANS_ID'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "CLIENT_CODE" OPTIONS (
    "column_name" 'CLIENT_CODE'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "ACCOUNT" OPTIONS (
    "column_name" 'ACCOUNT'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "ACTION" OPTIONS (
    "column_name" 'ACTION'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "CLASSCODE" OPTIONS (
    "column_name" 'CLASSCODE'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "SECCODE" OPTIONS (
    "column_name" 'SECCODE'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "OPERATION" OPTIONS (
    "column_name" 'OPERATION'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "PRICE" OPTIONS (
    "column_name" 'PRICE'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "QUANTITY" OPTIONS (
    "column_name" 'QUANTITY'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "COMMENT" OPTIONS (
    "column_name" 'COMMENT'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "TYPE" OPTIONS (
    "column_name" 'TYPE'
);
ALTER FOREIGN TABLE "mos"."orders_in" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);


ALTER FOREIGN TABLE "mos"."orders_in" OWNER TO "postgres";

--
-- TOC entry 337 (class 1259 OID 35104)
-- Name: orders_in_tcs; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_in_tcs" (
    "index" bigint,
    "quantity" bigint,
    "direction" bigint,
    "account_id" "text",
    "order_type" bigint,
    "order_id" "text",
    "instrument_id" "text",
    "last_upd" timestamp without time zone,
    "comment" "text",
    "code" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_in_tcs'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "account_id" OPTIONS (
    "column_name" 'account_id'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "order_type" OPTIONS (
    "column_name" 'order_type'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "instrument_id" OPTIONS (
    "column_name" 'instrument_id'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."orders_in_tcs" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);


ALTER FOREIGN TABLE "mos"."orders_in_tcs" OWNER TO "postgres";

--
-- TOC entry 338 (class 1259 OID 35107)
-- Name: orders_my; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_my" (
    "id" integer NOT NULL,
    "activate_id" integer,
    "state" integer,
    "quantity" integer,
    "comment" character varying(128),
    "remains" integer,
    "stop_loss" double precision,
    "take_profit" double precision,
    "parent_id" integer,
    "barrier" double precision,
    "max_amount" integer,
    "pause" double precision,
    "code" character varying(32),
    "direction" integer,
    "pending_conf" integer,
    "pending_unconf" integer,
    "end_time" timestamp with time zone,
    "start_time" timestamp with time zone,
    "provider" character varying(8),
    "order_type" character varying(8),
    "barrier_bound" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_my'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "activate_id" OPTIONS (
    "column_name" 'activate_id'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "state" OPTIONS (
    "column_name" 'state'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "remains" OPTIONS (
    "column_name" 'remains'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "stop_loss" OPTIONS (
    "column_name" 'stop_loss'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "take_profit" OPTIONS (
    "column_name" 'take_profit'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "parent_id" OPTIONS (
    "column_name" 'parent_id'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "barrier" OPTIONS (
    "column_name" 'barrier'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "max_amount" OPTIONS (
    "column_name" 'max_amount'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "pause" OPTIONS (
    "column_name" 'pause'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "pending_conf" OPTIONS (
    "column_name" 'pending_conf'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "pending_unconf" OPTIONS (
    "column_name" 'pending_unconf'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "end_time" OPTIONS (
    "column_name" 'end_time'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "start_time" OPTIONS (
    "column_name" 'start_time'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "provider" OPTIONS (
    "column_name" 'provider'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "order_type" OPTIONS (
    "column_name" 'order_type'
);
ALTER FOREIGN TABLE "mos"."orders_my" ALTER COLUMN "barrier_bound" OPTIONS (
    "column_name" 'barrier_bound'
);


ALTER FOREIGN TABLE "mos"."orders_my" OWNER TO "postgres";

--
-- TOC entry 339 (class 1259 OID 35110)
-- Name: orders_out; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_out" (
    "index" bigint,
    "firm_id" "text",
    "order_flags" bigint,
    "date_time" timestamp without time zone,
    "sent_local_time" timestamp without time zone,
    "flags" bigint,
    "price" double precision,
    "time" bigint,
    "sec_code" "text",
    "trans_id" bigint,
    "status" bigint,
    "exchange_code" "text",
    "result_msg" "text",
    "first_ordernum" bigint,
    "quantity" double precision,
    "uid" bigint,
    "brokerref" "text",
    "account" "text",
    "client_code" "text",
    "balance" double precision,
    "got_local_time" timestamp without time zone,
    "order_num" bigint,
    "gate_reply_time" timestamp without time zone,
    "server_trans_id" bigint,
    "error_source" bigint,
    "error_code" bigint,
    "class_code" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_out'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "firm_id" OPTIONS (
    "column_name" 'firm_id'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "order_flags" OPTIONS (
    "column_name" 'order_flags'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "date_time" OPTIONS (
    "column_name" 'date_time'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "sent_local_time" OPTIONS (
    "column_name" 'sent_local_time'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "flags" OPTIONS (
    "column_name" 'flags'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "sec_code" OPTIONS (
    "column_name" 'sec_code'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "trans_id" OPTIONS (
    "column_name" 'trans_id'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "status" OPTIONS (
    "column_name" 'status'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "exchange_code" OPTIONS (
    "column_name" 'exchange_code'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "result_msg" OPTIONS (
    "column_name" 'result_msg'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "first_ordernum" OPTIONS (
    "column_name" 'first_ordernum'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "uid" OPTIONS (
    "column_name" 'uid'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "brokerref" OPTIONS (
    "column_name" 'brokerref'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "account" OPTIONS (
    "column_name" 'account'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "client_code" OPTIONS (
    "column_name" 'client_code'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "balance" OPTIONS (
    "column_name" 'balance'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "got_local_time" OPTIONS (
    "column_name" 'got_local_time'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "order_num" OPTIONS (
    "column_name" 'order_num'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "gate_reply_time" OPTIONS (
    "column_name" 'gate_reply_time'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "server_trans_id" OPTIONS (
    "column_name" 'server_trans_id'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "error_source" OPTIONS (
    "column_name" 'error_source'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "error_code" OPTIONS (
    "column_name" 'error_code'
);
ALTER FOREIGN TABLE "mos"."orders_out" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);


ALTER FOREIGN TABLE "mos"."orders_out" OWNER TO "postgres";

--
-- TOC entry 340 (class 1259 OID 35113)
-- Name: orders_out_tcs; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."orders_out_tcs" (
    "index" bigint,
    "order_id" "text",
    "order_id_in" "text",
    "execution_report_status" bigint,
    "lots_requested" bigint,
    "lots_executed" bigint,
    "figi" "text",
    "direction" bigint,
    "order_type" bigint,
    "message" "text",
    "instrument_uid" "text",
    "initial_order_price" "text",
    "executed_order_price" "text",
    "total_order_amount" "text",
    "initial_commission" "text",
    "executed_commission" "text",
    "aci_value" "text",
    "initial_security_price" "text",
    "initial_order_price_pt" "text",
    "code" "text",
    "comment" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'orders_out_tcs'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "order_id" OPTIONS (
    "column_name" 'order_id'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "order_id_in" OPTIONS (
    "column_name" 'order_id_in'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "execution_report_status" OPTIONS (
    "column_name" 'execution_report_status'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "lots_requested" OPTIONS (
    "column_name" 'lots_requested'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "lots_executed" OPTIONS (
    "column_name" 'lots_executed'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "figi" OPTIONS (
    "column_name" 'figi'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "order_type" OPTIONS (
    "column_name" 'order_type'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "message" OPTIONS (
    "column_name" 'message'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "instrument_uid" OPTIONS (
    "column_name" 'instrument_uid'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "initial_order_price" OPTIONS (
    "column_name" 'initial_order_price'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "executed_order_price" OPTIONS (
    "column_name" 'executed_order_price'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "total_order_amount" OPTIONS (
    "column_name" 'total_order_amount'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "initial_commission" OPTIONS (
    "column_name" 'initial_commission'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "executed_commission" OPTIONS (
    "column_name" 'executed_commission'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "aci_value" OPTIONS (
    "column_name" 'aci_value'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "initial_security_price" OPTIONS (
    "column_name" 'initial_security_price'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "initial_order_price_pt" OPTIONS (
    "column_name" 'initial_order_price_pt'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."orders_out_tcs" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);


ALTER FOREIGN TABLE "mos"."orders_out_tcs" OWNER TO "postgres";

--
-- TOC entry 341 (class 1259 OID 35116)
-- Name: pos_bollinger; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_bollinger" (
    "code" character varying(16),
    "pos" bigint,
    "buy" bigint,
    "sell" bigint,
    "pnl" double precision,
    "price_balance" double precision,
    "volume" double precision,
    "firm" character varying,
    "bollinger" double precision,
    "count" bigint,
    "up" double precision,
    "down" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_bollinger'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "buy" OPTIONS (
    "column_name" 'buy'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "sell" OPTIONS (
    "column_name" 'sell'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "price_balance" OPTIONS (
    "column_name" 'price_balance'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "firm" OPTIONS (
    "column_name" 'firm'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "bollinger" OPTIONS (
    "column_name" 'bollinger'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "up" OPTIONS (
    "column_name" 'up'
);
ALTER FOREIGN TABLE "mos"."pos_bollinger" ALTER COLUMN "down" OPTIONS (
    "column_name" 'down'
);


ALTER FOREIGN TABLE "mos"."pos_bollinger" OWNER TO "postgres";

--
-- TOC entry 342 (class 1259 OID 35119)
-- Name: pos_collat; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_collat" (
    "instrument" character varying(32),
    "view" character varying(8),
    "type" character varying(8),
    "pos" bigint,
    "collateral" double precision,
    "account" character varying(32),
    "code" character varying(16),
    "volume" double precision,
    "dlong" double precision,
    "dshort" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_collat'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "instrument" OPTIONS (
    "column_name" 'instrument'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "view" OPTIONS (
    "column_name" 'view'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "collateral" OPTIONS (
    "column_name" 'collateral'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "account" OPTIONS (
    "column_name" 'account'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "dlong" OPTIONS (
    "column_name" 'dlong'
);
ALTER FOREIGN TABLE "mos"."pos_collat" ALTER COLUMN "dshort" OPTIONS (
    "column_name" 'dshort'
);


ALTER FOREIGN TABLE "mos"."pos_collat" OWNER TO "postgres";

--
-- TOC entry 343 (class 1259 OID 35122)
-- Name: pos_eq; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_eq" (
    "instrument" character varying(32),
    "pos" bigint,
    "price" double precision,
    "volume" double precision,
    "pnl" double precision,
    "buy" bigint,
    "sell" bigint,
    "tobuy" bigint,
    "tosell" bigint,
    "firm" character varying(32),
    "account" character varying(32),
    "client_id" character varying(32),
    "settlement" character varying(4),
    "code" character varying(16)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_eq'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "instrument" OPTIONS (
    "column_name" 'instrument'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "buy" OPTIONS (
    "column_name" 'buy'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "sell" OPTIONS (
    "column_name" 'sell'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "tobuy" OPTIONS (
    "column_name" 'tobuy'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "tosell" OPTIONS (
    "column_name" 'tosell'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "firm" OPTIONS (
    "column_name" 'firm'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "account" OPTIONS (
    "column_name" 'account'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "client_id" OPTIONS (
    "column_name" 'client_id'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "settlement" OPTIONS (
    "column_name" 'settlement'
);
ALTER FOREIGN TABLE "mos"."pos_eq" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);


ALTER FOREIGN TABLE "mos"."pos_eq" OWNER TO "postgres";

--
-- TOC entry 344 (class 1259 OID 35125)
-- Name: pos_fut; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_fut" (
    "code" character varying(16),
    "instrument" character varying(32),
    "maturity" "date",
    "pos" bigint,
    "buy" bigint,
    "sell" bigint,
    "pnl" double precision,
    "price_balance" double precision,
    "firm" character varying(16),
    "account" character varying(16),
    "type" character varying(16)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_fut'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "instrument" OPTIONS (
    "column_name" 'instrument'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "maturity" OPTIONS (
    "column_name" 'maturity'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "buy" OPTIONS (
    "column_name" 'buy'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "sell" OPTIONS (
    "column_name" 'sell'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "price_balance" OPTIONS (
    "column_name" 'price_balance'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "firm" OPTIONS (
    "column_name" 'firm'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "account" OPTIONS (
    "column_name" 'account'
);
ALTER FOREIGN TABLE "mos"."pos_fut" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);


ALTER FOREIGN TABLE "mos"."pos_fut" OWNER TO "postgres";

--
-- TOC entry 345 (class 1259 OID 35128)
-- Name: pos_money; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_money" (
    "money_prev" double precision,
    "money" double precision,
    "pos_current" double precision,
    "pos_plan" double precision,
    "pnl" double precision,
    "pnl_prev" double precision,
    "fees" double precision,
    "firm" character varying(16),
    "account" character varying(16),
    "type" character varying(16)
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_money'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "money_prev" OPTIONS (
    "column_name" 'money_prev'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "money" OPTIONS (
    "column_name" 'money'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "pos_current" OPTIONS (
    "column_name" 'pos_current'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "pos_plan" OPTIONS (
    "column_name" 'pos_plan'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "pnl_prev" OPTIONS (
    "column_name" 'pnl_prev'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "fees" OPTIONS (
    "column_name" 'fees'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "firm" OPTIONS (
    "column_name" 'firm'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "account" OPTIONS (
    "column_name" 'account'
);
ALTER FOREIGN TABLE "mos"."pos_money" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);


ALTER FOREIGN TABLE "mos"."pos_money" OWNER TO "postgres";

--
-- TOC entry 346 (class 1259 OID 35131)
-- Name: pos_volmult; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."pos_volmult" (
    "code" character varying NOT NULL,
    "multiplier" double precision NOT NULL
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'pos_volmult'
);
ALTER FOREIGN TABLE "mos"."pos_volmult" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."pos_volmult" ALTER COLUMN "multiplier" OPTIONS (
    "column_name" 'multiplier'
);


ALTER FOREIGN TABLE "mos"."pos_volmult" OWNER TO "postgres";

--
-- TOC entry 347 (class 1259 OID 35134)
-- Name: potential; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."potential" (
    "potential" double precision,
    "max" double precision,
    "price" double precision,
    "leverage" double precision,
    "code" character varying,
    "potential_sharp" double precision,
    "sigma" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'potential'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "potential" OPTIONS (
    "column_name" 'potential'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "leverage" OPTIONS (
    "column_name" 'leverage'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "potential_sharp" OPTIONS (
    "column_name" 'potential_sharp'
);
ALTER FOREIGN TABLE "mos"."potential" ALTER COLUMN "sigma" OPTIONS (
    "column_name" 'sigma'
);


ALTER FOREIGN TABLE "mos"."potential" OWNER TO "postgres";

--
-- TOC entry 348 (class 1259 OID 35137)
-- Name: public.df_monitor; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."public.df_monitor" (
    "level_0" bigint,
    "index" bigint,
    "code" "text",
    "old_state" "text",
    "old_price" double precision,
    "old_start" double precision,
    "old_end" double precision,
    "new_state" "text",
    "new_price" double precision,
    "new_start" double precision,
    "new_end" double precision,
    "std" double precision,
    "old_timestamp" timestamp with time zone,
    "new_timestamp" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'public.df_monitor'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "level_0" OPTIONS (
    "column_name" 'level_0'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "old_state" OPTIONS (
    "column_name" 'old_state'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "old_price" OPTIONS (
    "column_name" 'old_price'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "old_start" OPTIONS (
    "column_name" 'old_start'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "old_end" OPTIONS (
    "column_name" 'old_end'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "new_state" OPTIONS (
    "column_name" 'new_state'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "new_price" OPTIONS (
    "column_name" 'new_price'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "new_start" OPTIONS (
    "column_name" 'new_start'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "new_end" OPTIONS (
    "column_name" 'new_end'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "old_timestamp" OPTIONS (
    "column_name" 'old_timestamp'
);
ALTER FOREIGN TABLE "mos"."public.df_monitor" ALTER COLUMN "new_timestamp" OPTIONS (
    "column_name" 'new_timestamp'
);


ALTER FOREIGN TABLE "mos"."public.df_monitor" OWNER TO "postgres";

--
-- TOC entry 349 (class 1259 OID 35140)
-- Name: quote_bollinger; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."quote_bollinger" (
    "code" character varying(16),
    "class_code" "text",
    "quote" double precision,
    "bollinger" double precision,
    "count" bigint,
    "up" double precision,
    "down" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'quote_bollinger'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "quote" OPTIONS (
    "column_name" 'quote'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "bollinger" OPTIONS (
    "column_name" 'bollinger'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "up" OPTIONS (
    "column_name" 'up'
);
ALTER FOREIGN TABLE "mos"."quote_bollinger" ALTER COLUMN "down" OPTIONS (
    "column_name" 'down'
);


ALTER FOREIGN TABLE "mos"."quote_bollinger" OWNER TO "postgres";

--
-- TOC entry 350 (class 1259 OID 35143)
-- Name: report_big_deals; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_big_deals" (
    "net_amount" double precision,
    "datetime" timestamp without time zone,
    "code" character varying(32),
    "max_price" double precision,
    "min_price" double precision,
    "shift_abs" double precision,
    "open_interest_diff" integer
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_big_deals'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "net_amount" OPTIONS (
    "column_name" 'net_amount'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "max_price" OPTIONS (
    "column_name" 'max_price'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "min_price" OPTIONS (
    "column_name" 'min_price'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "shift_abs" OPTIONS (
    "column_name" 'shift_abs'
);
ALTER FOREIGN TABLE "mos"."report_big_deals" ALTER COLUMN "open_interest_diff" OPTIONS (
    "column_name" 'open_interest_diff'
);


ALTER FOREIGN TABLE "mos"."report_big_deals" OWNER TO "postgres";

--
-- TOC entry 351 (class 1259 OID 35146)
-- Name: report_deal_imp; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_deal_imp" (
    "datetime" timestamp without time zone,
    "code" character varying(32),
    "price" double precision,
    "net_amount" numeric,
    "total_amount" numeric,
    "avg_open_interest" numeric
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_deal_imp'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "net_amount" OPTIONS (
    "column_name" 'net_amount'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "total_amount" OPTIONS (
    "column_name" 'total_amount'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp" ALTER COLUMN "avg_open_interest" OPTIONS (
    "column_name" 'avg_open_interest'
);


ALTER FOREIGN TABLE "mos"."report_deal_imp" OWNER TO "postgres";

--
-- TOC entry 352 (class 1259 OID 35149)
-- Name: report_deal_imp_arch; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_deal_imp_arch" (
    "datetime" timestamp without time zone,
    "code" character varying(32),
    "price" double precision,
    "net_amount" numeric,
    "total_amount" numeric,
    "avg_open_interest" numeric
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_deal_imp_arch'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "net_amount" OPTIONS (
    "column_name" 'net_amount'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "total_amount" OPTIONS (
    "column_name" 'total_amount'
);
ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" ALTER COLUMN "avg_open_interest" OPTIONS (
    "column_name" 'avg_open_interest'
);


ALTER FOREIGN TABLE "mos"."report_deal_imp_arch" OWNER TO "postgres";

--
-- TOC entry 353 (class 1259 OID 35152)
-- Name: report_plita; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_plita" (
    "price" "text",
    "quantity" bigint,
    "ba" "text",
    "datetime" timestamp with time zone,
    "code" "text",
    "abnormal" boolean,
    "limit" double precision,
    "minutes" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_plita'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "ba" OPTIONS (
    "column_name" 'ba'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "abnormal" OPTIONS (
    "column_name" 'abnormal'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "limit" OPTIONS (
    "column_name" 'limit'
);
ALTER FOREIGN TABLE "mos"."report_plita" ALTER COLUMN "minutes" OPTIONS (
    "column_name" 'minutes'
);


ALTER FOREIGN TABLE "mos"."report_plita" OWNER TO "postgres";

--
-- TOC entry 354 (class 1259 OID 35155)
-- Name: report_volumes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_volumes" (
    "security" character varying(64),
    "class_code" character varying(64),
    "datetime" timestamp with time zone,
    "volume" integer,
    "close" double precision,
    "crnt_close" double precision,
    "prev_close" double precision,
    "crnt_time" timestamp with time zone,
    "money_volume" double precision,
    "daily_diff" double precision,
    "diff" double precision,
    "points_num" bigint,
    "volume_std" numeric,
    "volume_avg" bigint,
    "volume_avg_10" numeric,
    "money_volume_avg" double precision,
    "money_volume_avg_10" double precision,
    "diff_mean" double precision,
    "diff_mean_10" double precision,
    "diff_std" double precision,
    "diff_std_10" double precision,
    "diff_prct_mean" double precision,
    "diff_prct_mean_10" double precision,
    "diff_prct_std" double precision,
    "diff_prct_std_10" double precision,
    "cnt_days" bigint,
    "max_dt" "date",
    "max_datetime" timestamp with time zone,
    "volume_last" integer,
    "money_volume_last" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_volumes'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "datetime" OPTIONS (
    "column_name" 'datetime'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "close" OPTIONS (
    "column_name" 'close'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "crnt_close" OPTIONS (
    "column_name" 'crnt_close'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "prev_close" OPTIONS (
    "column_name" 'prev_close'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "crnt_time" OPTIONS (
    "column_name" 'crnt_time'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "money_volume" OPTIONS (
    "column_name" 'money_volume'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "daily_diff" OPTIONS (
    "column_name" 'daily_diff'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff" OPTIONS (
    "column_name" 'diff'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "points_num" OPTIONS (
    "column_name" 'points_num'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "volume_std" OPTIONS (
    "column_name" 'volume_std'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "volume_avg" OPTIONS (
    "column_name" 'volume_avg'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "volume_avg_10" OPTIONS (
    "column_name" 'volume_avg_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "money_volume_avg" OPTIONS (
    "column_name" 'money_volume_avg'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "money_volume_avg_10" OPTIONS (
    "column_name" 'money_volume_avg_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_mean" OPTIONS (
    "column_name" 'diff_mean'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_mean_10" OPTIONS (
    "column_name" 'diff_mean_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_std" OPTIONS (
    "column_name" 'diff_std'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_std_10" OPTIONS (
    "column_name" 'diff_std_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_prct_mean" OPTIONS (
    "column_name" 'diff_prct_mean'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_prct_mean_10" OPTIONS (
    "column_name" 'diff_prct_mean_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_prct_std" OPTIONS (
    "column_name" 'diff_prct_std'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "diff_prct_std_10" OPTIONS (
    "column_name" 'diff_prct_std_10'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "cnt_days" OPTIONS (
    "column_name" 'cnt_days'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "max_dt" OPTIONS (
    "column_name" 'max_dt'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "max_datetime" OPTIONS (
    "column_name" 'max_datetime'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "volume_last" OPTIONS (
    "column_name" 'volume_last'
);
ALTER FOREIGN TABLE "mos"."report_volumes" ALTER COLUMN "money_volume_last" OPTIONS (
    "column_name" 'money_volume_last'
);


ALTER FOREIGN TABLE "mos"."report_volumes" OWNER TO "postgres";

--
-- TOC entry 355 (class 1259 OID 35158)
-- Name: report_volumes_agg; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."report_volumes_agg" (
    "security" character varying(64),
    "class_code" character varying(64),
    "time" timestamp with time zone,
    "price" double precision,
    "ytd_price" double precision,
    "ytd_time" timestamp with time zone,
    "inc" double precision,
    "td_mvolume" double precision,
    "ytd_mvolume" double precision,
    "avg_mvolume" double precision,
    "mvolume_inc" double precision,
    "mvolume_inc_avg" double precision,
    "td_volume" bigint,
    "ytd_volume" bigint,
    "avg_volume" numeric,
    "volume_inc" bigint,
    "volume_inc_avg" numeric,
    "avg" numeric,
    "max" "date"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'report_volumes_agg'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "security" OPTIONS (
    "column_name" 'security'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "ytd_price" OPTIONS (
    "column_name" 'ytd_price'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "ytd_time" OPTIONS (
    "column_name" 'ytd_time'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "inc" OPTIONS (
    "column_name" 'inc'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "td_mvolume" OPTIONS (
    "column_name" 'td_mvolume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "ytd_mvolume" OPTIONS (
    "column_name" 'ytd_mvolume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "avg_mvolume" OPTIONS (
    "column_name" 'avg_mvolume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "mvolume_inc" OPTIONS (
    "column_name" 'mvolume_inc'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "mvolume_inc_avg" OPTIONS (
    "column_name" 'mvolume_inc_avg'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "td_volume" OPTIONS (
    "column_name" 'td_volume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "ytd_volume" OPTIONS (
    "column_name" 'ytd_volume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "avg_volume" OPTIONS (
    "column_name" 'avg_volume'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "volume_inc_avg" OPTIONS (
    "column_name" 'volume_inc_avg'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "avg" OPTIONS (
    "column_name" 'avg'
);
ALTER FOREIGN TABLE "mos"."report_volumes_agg" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);


ALTER FOREIGN TABLE "mos"."report_volumes_agg" OWNER TO "postgres";

--
-- TOC entry 356 (class 1259 OID 35161)
-- Name: secquotes; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."secquotes" (
    "fullid" character varying(128),
    "instrumentid" character varying(32),
    "type" character varying(16),
    "code" character varying(16),
    "tradedate" character varying(12),
    "currency" character varying(8),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "lastprice" double precision,
    "volume" double precision,
    "prctchange" double precision,
    "lastdealtime" character varying(32),
    "session" character varying(32),
    "listing" integer,
    "valuedate" character varying(16),
    "isin" character varying(16),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "updated_at" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'secquotes'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "fullid" OPTIONS (
    "column_name" 'fullid'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "instrumentid" OPTIONS (
    "column_name" 'instrumentid'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "currency" OPTIONS (
    "column_name" 'currency'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "lastprice" OPTIONS (
    "column_name" 'lastprice'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "prctchange" OPTIONS (
    "column_name" 'prctchange'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "lastdealtime" OPTIONS (
    "column_name" 'lastdealtime'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "session" OPTIONS (
    "column_name" 'session'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "listing" OPTIONS (
    "column_name" 'listing'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "valuedate" OPTIONS (
    "column_name" 'valuedate'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "isin" OPTIONS (
    "column_name" 'isin'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "prec" OPTIONS (
    "column_name" 'prec'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "pricestep" OPTIONS (
    "column_name" 'pricestep'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "lastdealqty" OPTIONS (
    "column_name" 'lastdealqty'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "lastdealvol" OPTIONS (
    "column_name" 'lastdealvol'
);
ALTER FOREIGN TABLE "mos"."secquotes" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);


ALTER FOREIGN TABLE "mos"."secquotes" OWNER TO "postgres";

--
-- TOC entry 357 (class 1259 OID 35164)
-- Name: secquotesdiff; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."secquotesdiff" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'secquotesdiff'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."secquotesdiff" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);


ALTER FOREIGN TABLE "mos"."secquotesdiff" OWNER TO "postgres";

--
-- TOC entry 358 (class 1259 OID 35167)
-- Name: secquotesdiffhist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."secquotesdiffhist" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'secquotesdiffhist'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "volume_inc" OPTIONS (
    "column_name" 'volume_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "bid_inc" OPTIONS (
    "column_name" 'bid_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "ask_inc" OPTIONS (
    "column_name" 'ask_inc'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "last_upd" OPTIONS (
    "column_name" 'last_upd'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "volume_wa" OPTIONS (
    "column_name" 'volume_wa'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "min_5mins" OPTIONS (
    "column_name" 'min_5mins'
);
ALTER FOREIGN TABLE "mos"."secquotesdiffhist" ALTER COLUMN "max_5mins" OPTIONS (
    "column_name" 'max_5mins'
);


ALTER FOREIGN TABLE "mos"."secquotesdiffhist" OWNER TO "postgres";

--
-- TOC entry 359 (class 1259 OID 35170)
-- Name: secquoteshist; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."secquoteshist" (
    "fullid" character varying(128),
    "instrumentid" character varying(32),
    "type" character varying(16),
    "code" character varying(16),
    "tradedate" character varying(12),
    "currency" character varying(8),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "lastprice" double precision,
    "volume" double precision,
    "prctchange" double precision,
    "lastdealtime" character varying(32),
    "session" character varying(32),
    "listing" integer,
    "valuedate" character varying(16),
    "isin" character varying(16),
    "timestamp" time with time zone,
    "snaptimestamp" time with time zone,
    "lot" integer,
    "prec" bigint,
    "pricestep" double precision,
    "lastdealqty" double precision,
    "lastdealvol" double precision,
    "updated_at" timestamp with time zone
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'secquoteshist'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "fullid" OPTIONS (
    "column_name" 'fullid'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "instrumentid" OPTIONS (
    "column_name" 'instrumentid'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "tradedate" OPTIONS (
    "column_name" 'tradedate'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "currency" OPTIONS (
    "column_name" 'currency'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "bidamount" OPTIONS (
    "column_name" 'bidamount'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "askamount" OPTIONS (
    "column_name" 'askamount'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "lastprice" OPTIONS (
    "column_name" 'lastprice'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "prctchange" OPTIONS (
    "column_name" 'prctchange'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "lastdealtime" OPTIONS (
    "column_name" 'lastdealtime'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "session" OPTIONS (
    "column_name" 'session'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "listing" OPTIONS (
    "column_name" 'listing'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "valuedate" OPTIONS (
    "column_name" 'valuedate'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "isin" OPTIONS (
    "column_name" 'isin'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "timestamp" OPTIONS (
    "column_name" 'timestamp'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "snaptimestamp" OPTIONS (
    "column_name" 'snaptimestamp'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "prec" OPTIONS (
    "column_name" 'prec'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "pricestep" OPTIONS (
    "column_name" 'pricestep'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "lastdealqty" OPTIONS (
    "column_name" 'lastdealqty'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "lastdealvol" OPTIONS (
    "column_name" 'lastdealvol'
);
ALTER FOREIGN TABLE "mos"."secquoteshist" ALTER COLUMN "updated_at" OPTIONS (
    "column_name" 'updated_at'
);


ALTER FOREIGN TABLE "mos"."secquoteshist" OWNER TO "postgres";

--
-- TOC entry 360 (class 1259 OID 35173)
-- Name: signal; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."signal" (
    "tstz" timestamp with time zone,
    "code" character varying(32),
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(32),
    "news_time" timestamp with time zone,
    "min_val" double precision,
    "max_val" double precision,
    "mean_val" double precision,
    "volume" double precision,
    "board" "text",
    "min" double precision,
    "max" double precision,
    "last_volume" double precision,
    "count" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'signal'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "tstz" OPTIONS (
    "column_name" 'tstz'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "date_discovery" OPTIONS (
    "column_name" 'date_discovery'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "channel_source" OPTIONS (
    "column_name" 'channel_source'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "news_time" OPTIONS (
    "column_name" 'news_time'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "min_val" OPTIONS (
    "column_name" 'min_val'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "max_val" OPTIONS (
    "column_name" 'max_val'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "mean_val" OPTIONS (
    "column_name" 'mean_val'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "last_volume" OPTIONS (
    "column_name" 'last_volume'
);
ALTER FOREIGN TABLE "mos"."signal" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);


ALTER FOREIGN TABLE "mos"."signal" OWNER TO "postgres";

--
-- TOC entry 361 (class 1259 OID 35176)
-- Name: signal_arch; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."signal_arch" (
    "id" integer NOT NULL,
    "tstz" timestamp with time zone,
    "code" character varying(16),
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(64),
    "news_time" timestamp with time zone,
    "min_val" double precision,
    "max_val" double precision,
    "mean_val" double precision,
    "volume" double precision,
    "board" character varying(32),
    "min" double precision,
    "max" double precision,
    "last_volume" double precision,
    "count" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'signal_arch'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "id" OPTIONS (
    "column_name" 'id'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "tstz" OPTIONS (
    "column_name" 'tstz'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "date_discovery" OPTIONS (
    "column_name" 'date_discovery'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "channel_source" OPTIONS (
    "column_name" 'channel_source'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "news_time" OPTIONS (
    "column_name" 'news_time'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "min_val" OPTIONS (
    "column_name" 'min_val'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "max_val" OPTIONS (
    "column_name" 'max_val'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "mean_val" OPTIONS (
    "column_name" 'mean_val'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "board" OPTIONS (
    "column_name" 'board'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "min" OPTIONS (
    "column_name" 'min'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "max" OPTIONS (
    "column_name" 'max'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "last_volume" OPTIONS (
    "column_name" 'last_volume'
);
ALTER FOREIGN TABLE "mos"."signal_arch" ALTER COLUMN "count" OPTIONS (
    "column_name" 'count'
);


ALTER FOREIGN TABLE "mos"."signal_arch" OWNER TO "postgres";

--
-- TOC entry 362 (class 1259 OID 35179)
-- Name: tinkoff_params; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."tinkoff_params" (
    "index" bigint,
    "name" "text",
    "ticker" "text",
    "class_code" "text",
    "figi" "text",
    "type" "text",
    "min_price_increment" "text",
    "currency" "text",
    "exchange" "text"
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'tinkoff_params'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "index" OPTIONS (
    "column_name" 'index'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "name" OPTIONS (
    "column_name" 'name'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "ticker" OPTIONS (
    "column_name" 'ticker'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "class_code" OPTIONS (
    "column_name" 'class_code'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "figi" OPTIONS (
    "column_name" 'figi'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "type" OPTIONS (
    "column_name" 'type'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "min_price_increment" OPTIONS (
    "column_name" 'min_price_increment'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "currency" OPTIONS (
    "column_name" 'currency'
);
ALTER FOREIGN TABLE "mos"."tinkoff_params" ALTER COLUMN "exchange" OPTIONS (
    "column_name" 'exchange'
);


ALTER FOREIGN TABLE "mos"."tinkoff_params" OWNER TO "postgres";

--
-- TOC entry 363 (class 1259 OID 35182)
-- Name: trd_mypos; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."trd_mypos" (
    "code" character varying,
    "pos" bigint,
    "pnl" double precision,
    "mktprice" double precision,
    "volume" double precision,
    "lower" numeric,
    "upper" numeric,
    "levels" numeric,
    "new_state" "text",
    "ordnum" bigint,
    "actnum" bigint,
    "bid" "text",
    "bid_qty" bigint,
    "ask" "text",
    "ask_qty" bigint
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'trd_mypos'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "mktprice" OPTIONS (
    "column_name" 'mktprice'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "lower" OPTIONS (
    "column_name" 'lower'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "upper" OPTIONS (
    "column_name" 'upper'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "levels" OPTIONS (
    "column_name" 'levels'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "new_state" OPTIONS (
    "column_name" 'new_state'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "ordnum" OPTIONS (
    "column_name" 'ordnum'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "actnum" OPTIONS (
    "column_name" 'actnum'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "bid" OPTIONS (
    "column_name" 'bid'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "bid_qty" OPTIONS (
    "column_name" 'bid_qty'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "ask" OPTIONS (
    "column_name" 'ask'
);
ALTER FOREIGN TABLE "mos"."trd_mypos" ALTER COLUMN "ask_qty" OPTIONS (
    "column_name" 'ask_qty'
);


ALTER FOREIGN TABLE "mos"."trd_mypos" OWNER TO "postgres";

--
-- TOC entry 364 (class 1259 OID 35185)
-- Name: trd_pos; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."trd_pos" (
    "state" integer,
    "quantity" integer,
    "comment" "text",
    "stop_loss" double precision,
    "take_profit" double precision,
    "barrier" double precision,
    "max_amount" integer,
    "pause" integer,
    "code" "text",
    "direction" integer,
    "end_time" timestamp with time zone,
    "start_time" timestamp with time zone,
    "new_state" "text",
    "new_price" double precision,
    "new_start" double precision,
    "new_end" double precision,
    "std" double precision,
    "next_resistance" double precision,
    "prev_resistance_std" double precision,
    "sl" double precision,
    "prev_resistance" double precision,
    "preprev_resistance" "text",
    "prev_take_profit" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'trd_pos'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "state" OPTIONS (
    "column_name" 'state'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "quantity" OPTIONS (
    "column_name" 'quantity'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "comment" OPTIONS (
    "column_name" 'comment'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "stop_loss" OPTIONS (
    "column_name" 'stop_loss'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "take_profit" OPTIONS (
    "column_name" 'take_profit'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "barrier" OPTIONS (
    "column_name" 'barrier'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "max_amount" OPTIONS (
    "column_name" 'max_amount'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "pause" OPTIONS (
    "column_name" 'pause'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "direction" OPTIONS (
    "column_name" 'direction'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "end_time" OPTIONS (
    "column_name" 'end_time'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "start_time" OPTIONS (
    "column_name" 'start_time'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "new_state" OPTIONS (
    "column_name" 'new_state'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "new_price" OPTIONS (
    "column_name" 'new_price'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "new_start" OPTIONS (
    "column_name" 'new_start'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "new_end" OPTIONS (
    "column_name" 'new_end'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "std" OPTIONS (
    "column_name" 'std'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "next_resistance" OPTIONS (
    "column_name" 'next_resistance'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "prev_resistance_std" OPTIONS (
    "column_name" 'prev_resistance_std'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "sl" OPTIONS (
    "column_name" 'sl'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "prev_resistance" OPTIONS (
    "column_name" 'prev_resistance'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "preprev_resistance" OPTIONS (
    "column_name" 'preprev_resistance'
);
ALTER FOREIGN TABLE "mos"."trd_pos" ALTER COLUMN "prev_take_profit" OPTIONS (
    "column_name" 'prev_take_profit'
);


ALTER FOREIGN TABLE "mos"."trd_pos" OWNER TO "postgres";

--
-- TOC entry 365 (class 1259 OID 35188)
-- Name: united_pos; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."united_pos" (
    "code" character varying(16),
    "pos" bigint,
    "buy" bigint,
    "sell" bigint,
    "pnl" double precision,
    "price_balance" double precision,
    "volume" double precision,
    "firm" character varying
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'united_pos'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "pos" OPTIONS (
    "column_name" 'pos'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "buy" OPTIONS (
    "column_name" 'buy'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "sell" OPTIONS (
    "column_name" 'sell'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "price_balance" OPTIONS (
    "column_name" 'price_balance'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."united_pos" ALTER COLUMN "firm" OPTIONS (
    "column_name" 'firm'
);


ALTER FOREIGN TABLE "mos"."united_pos" OWNER TO "postgres";

--
-- TOC entry 366 (class 1259 OID 35191)
-- Name: vpnl; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."vpnl" (
    "time" time without time zone,
    "amount" bigint,
    "code" character varying(32),
    "in_price" double precision,
    "price" double precision,
    "volume" double precision,
    "broker_fees" double precision,
    "pnl" double precision,
    "lot" integer
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'vpnl'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "time" OPTIONS (
    "column_name" 'time'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "in_price" OPTIONS (
    "column_name" 'in_price'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "price" OPTIONS (
    "column_name" 'price'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "broker_fees" OPTIONS (
    "column_name" 'broker_fees'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."vpnl" ALTER COLUMN "lot" OPTIONS (
    "column_name" 'lot'
);


ALTER FOREIGN TABLE "mos"."vpnl" OWNER TO "postgres";

--
-- TOC entry 367 (class 1259 OID 35194)
-- Name: vpnlext; Type: FOREIGN TABLE; Schema: mos; Owner: postgres
--

CREATE FOREIGN TABLE "mos"."vpnlext" (
    "amount" numeric,
    "code" character varying(32),
    "mprice" double precision,
    "pnl" double precision,
    "volume" double precision,
    "breakevenprice" double precision
)
SERVER "moscow"
OPTIONS (
    "schema_name" 'public',
    "table_name" 'vpnlext'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "amount" OPTIONS (
    "column_name" 'amount'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "code" OPTIONS (
    "column_name" 'code'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "mprice" OPTIONS (
    "column_name" 'mprice'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "pnl" OPTIONS (
    "column_name" 'pnl'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "volume" OPTIONS (
    "column_name" 'volume'
);
ALTER FOREIGN TABLE "mos"."vpnlext" ALTER COLUMN "breakevenprice" OPTIONS (
    "column_name" 'breakevenprice'
);


ALTER FOREIGN TABLE "mos"."vpnlext" OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- TOC entry 375 (class 1259 OID 149527)
-- Name: futquotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."futquotes" (
    "fullid" character varying(128) NOT NULL,
    "code" character varying(16),
    "status" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "collateral" double precision,
    "minprice" double precision,
    "maxprice" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "tillmaturity" integer,
    "maturitydate" character varying(16),
    "tradedate" character varying(12),
    "closeprice" double precision,
    "prctchange" double precision,
    "instrumentid" character varying(32),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "pricestepcur" double precision,
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."futquotes" OWNER TO "postgres";

--
-- TOC entry 374 (class 1259 OID 149520)
-- Name: secquotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."secquotes" (
    "fullid" character varying(128) NOT NULL,
    "instrumentid" character varying(32),
    "type" character varying(16),
    "code" character varying(16),
    "tradedate" character varying(12),
    "currency" character varying(8),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "lastprice" double precision,
    "volume" double precision,
    "prctchange" double precision,
    "lastdealtime" character varying(32),
    "session" character varying(32),
    "listing" integer,
    "valuedate" character varying(16),
    "isin" character varying(16),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."secquotes" OWNER TO "postgres";

--
-- TOC entry 376 (class 1259 OID 149558)
-- Name: allquotes_mini; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."allquotes_mini" AS
 SELECT "futquotes"."code",
    'SPBFUT'::"text" AS "market",
    "futquotes"."bid",
    "futquotes"."bidamount",
    "futquotes"."ask",
    "futquotes"."askamount",
    (("futquotes"."bid" + "futquotes"."ask") / (2)::double precision) AS "mid"
   FROM "public"."futquotes"
  WHERE ((("futquotes"."status")::integer = 1) AND ("futquotes"."bidamount" > (0)::double precision) AND ("futquotes"."askamount" > (0)::double precision))
UNION ALL
 SELECT "secquotes"."code",
    'TQBR'::"text" AS "market",
    "secquotes"."bid",
    "secquotes"."bidamount",
    "secquotes"."ask",
    "secquotes"."askamount",
    (("secquotes"."bid" + "secquotes"."ask") / (2)::double precision) AS "mid"
   FROM "public"."secquotes"
  WHERE (("secquotes"."bidamount" > (0)::double precision) AND ("secquotes"."askamount" > (0)::double precision) AND (("secquotes"."session")::integer = 1));


ALTER VIEW "public"."allquotes_mini" OWNER TO "postgres";

--
-- TOC entry 224 (class 1259 OID 16416)
-- Name: deorders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deorders" (
    "order_id" bigint,
    "tradedate" "date",
    "dateopen" "date",
    "timeopen" time without time zone,
    "datecancel" "date",
    "timecancel" time without time zone,
    "code" character varying(32),
    "instrument" character varying(32),
    "bs" character varying(16),
    "price" double precision,
    "orderamount" bigint,
    "orderremains" bigint,
    "orderexecuted" bigint,
    "volume" double precision,
    "comment" character varying(32),
    "type" character varying(16),
    "state" character varying(16),
    "volumecalc" double precision,
    "class_code" character varying(16),
    "cancelreason" "text",
    "execmode" character varying(16),
    "mcsopen" bigint,
    "mcscancel" bigint,
    "trans_id" bigint
);


ALTER TABLE "public"."deorders" OWNER TO "postgres";

--
-- TOC entry 225 (class 1259 OID 16421)
-- Name: orders_in; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_in" (
    "index" bigint,
    "TRANS_ID" "text",
    "CLIENT_CODE" "text",
    "ACCOUNT" "text",
    "ACTION" "text",
    "CLASSCODE" "text",
    "SECCODE" "text",
    "OPERATION" "text",
    "PRICE" "text",
    "QUANTITY" "text",
    "COMMENT" "text",
    "TYPE" "text",
    "last_upd" timestamp with time zone
);


ALTER TABLE "public"."orders_in" OWNER TO "postgres";

--
-- TOC entry 226 (class 1259 OID 16426)
-- Name: orders_out; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_out" (
    "index" bigint,
    "firm_id" "text",
    "order_flags" bigint,
    "date_time" timestamp without time zone,
    "sent_local_time" timestamp without time zone,
    "flags" bigint,
    "price" double precision,
    "time" bigint,
    "sec_code" "text",
    "trans_id" bigint,
    "status" bigint,
    "exchange_code" "text",
    "result_msg" "text",
    "first_ordernum" bigint,
    "quantity" double precision,
    "uid" bigint,
    "brokerref" "text",
    "account" "text",
    "client_code" "text",
    "balance" double precision,
    "got_local_time" timestamp without time zone,
    "order_num" bigint,
    "gate_reply_time" timestamp without time zone,
    "server_trans_id" bigint,
    "error_source" bigint,
    "error_code" bigint,
    "class_code" "text"
);


ALTER TABLE "public"."orders_out" OWNER TO "postgres";

--
-- TOC entry 227 (class 1259 OID 16431)
-- Name: autoorders; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."autoorders" AS
 SELECT "oin"."TRANS_ID",
    COALESCE("max_confirmed_id"."last_confirmed_id", (0)::bigint) AS "last_confirmed_id",
        CASE
            WHEN ((COALESCE("max_confirmed_id"."last_confirmed_id", (0)::bigint) < ("oin"."TRANS_ID")::bigint) AND ("oout"."status" IS NULL)) THEN ("oin"."QUANTITY")::bigint
            ELSE (0)::bigint
        END AS "unconfirmed_quantity",
    "oin"."ACCOUNT",
    "oin"."ACTION",
    "oin"."CLASSCODE",
    "oin"."SECCODE",
    "oin"."OPERATION",
    "oin"."PRICE",
    "oin"."COMMENT",
    "oin"."QUANTITY",
    "oin"."last_upd" AS "in_last_upd",
    "oout"."date_time",
    "oout"."sent_local_time",
    "oout"."time",
    "oout"."trans_id",
    "oout"."status",
    "oout"."result_msg",
    "oout"."quantity",
    "oout"."got_local_time",
    "oout"."order_num",
    "oout"."gate_reply_time",
    "oout"."error_source",
    "oout"."error_code",
    "dord"."trans_id" AS "ord_trans_id",
    "dord"."order_id",
    "dord"."tradedate",
    "dord"."dateopen",
    "dord"."timeopen",
    "dord"."datecancel",
    "dord"."timecancel",
    "dord"."orderremains",
    "dord"."orderexecuted",
    "dord"."volume",
    "dord"."state",
    "dord"."volumecalc",
    "dord"."cancelreason",
    "dord"."execmode"
   FROM (((( SELECT "orders_in"."TRANS_ID",
            "orders_in"."ACCOUNT",
            "orders_in"."ACTION",
            "orders_in"."CLASSCODE",
            "orders_in"."SECCODE",
            "orders_in"."OPERATION",
            "orders_in"."PRICE",
            "orders_in"."COMMENT",
            "orders_in"."QUANTITY",
            "orders_in"."last_upd"
           FROM "public"."orders_in") "oin"
     LEFT JOIN ( SELECT "orders_out"."date_time",
            "orders_out"."sent_local_time",
            "orders_out"."time",
            "orders_out"."trans_id",
            "orders_out"."status",
            "orders_out"."result_msg",
            "orders_out"."quantity",
            "orders_out"."got_local_time",
            "orders_out"."order_num",
            "orders_out"."gate_reply_time",
            "orders_out"."error_source",
            "orders_out"."error_code"
           FROM "public"."orders_out") "oout" ON ((("oin"."TRANS_ID")::bigint = "oout"."trans_id")))
     LEFT JOIN ( SELECT "deorders"."order_id",
            "deorders"."trans_id",
            "deorders"."tradedate",
            "deorders"."dateopen",
            "deorders"."timeopen",
            "deorders"."datecancel",
            "deorders"."timecancel",
            "deorders"."orderremains",
            "deorders"."orderexecuted",
            "deorders"."volume",
            "deorders"."state",
            "deorders"."volumecalc",
            "deorders"."cancelreason",
            "deorders"."execmode"
           FROM "public"."deorders") "dord" ON ((("oin"."TRANS_ID")::bigint = "dord"."trans_id")))
     LEFT JOIN ( SELECT "deorders"."code",
            "max"(COALESCE("deorders"."trans_id", (0)::bigint)) AS "last_confirmed_id"
           FROM "public"."deorders"
          GROUP BY "deorders"."code") "max_confirmed_id" ON (("oin"."SECCODE" = ("max_confirmed_id"."code")::"text")));


ALTER VIEW "public"."autoorders" OWNER TO "postgres";

--
-- TOC entry 228 (class 1259 OID 16436)
-- Name: autoorders_grouped; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."autoorders_grouped" AS
 SELECT "SECCODE" AS "code",
    "COMMENT" AS "comment",
    "sum"((COALESCE(("orderexecuted")::integer, 0) *
        CASE
            WHEN ("OPERATION" = 'S'::"text") THEN '-1'::integer
            WHEN ("OPERATION" = 'B'::"text") THEN 1
            ELSE 0
        END)) AS "amount",
    "sum"((COALESCE(("unconfirmed_quantity")::integer, 0) *
        CASE
            WHEN ("OPERATION" = 'S'::"text") THEN '-1'::integer
            WHEN ("OPERATION" = 'B'::"text") THEN 1
            ELSE 0
        END)) AS "unconfirmed_amount",
    "sum"(((COALESCE(("orderremains")::integer, 0) *
        CASE
            WHEN ("OPERATION" = 'S'::"text") THEN '-1'::integer
            WHEN ("OPERATION" = 'B'::"text") THEN 1
            ELSE 0
        END) *
        CASE
            WHEN (("state")::"text" = 'ACTIVE'::"text") THEN 1
            ELSE 0
        END)) AS "amount_pending"
   FROM "public"."autoorders"
  GROUP BY "SECCODE", "COMMENT";


ALTER VIEW "public"."autoorders_grouped" OWNER TO "postgres";

--
-- TOC entry 229 (class 1259 OID 16441)
-- Name: orders_in_tcs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_in_tcs" (
    "index" bigint,
    "quantity" bigint,
    "direction" bigint,
    "account_id" "text",
    "order_type" bigint,
    "order_id" "text",
    "instrument_id" "text",
    "last_upd" timestamp without time zone,
    "comment" "text",
    "code" "text"
);


ALTER TABLE "public"."orders_in_tcs" OWNER TO "postgres";

--
-- TOC entry 230 (class 1259 OID 16446)
-- Name: orders_out_tcs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_out_tcs" (
    "index" bigint,
    "order_id" "text",
    "order_id_in" "text",
    "execution_report_status" bigint,
    "lots_requested" bigint,
    "lots_executed" bigint,
    "figi" "text",
    "direction" bigint,
    "order_type" bigint,
    "message" "text",
    "instrument_uid" "text",
    "initial_order_price" "text",
    "executed_order_price" "text",
    "total_order_amount" "text",
    "initial_commission" "text",
    "executed_commission" "text",
    "aci_value" "text",
    "initial_security_price" "text",
    "initial_order_price_pt" "text",
    "code" "text",
    "comment" "text"
);


ALTER TABLE "public"."orders_out_tcs" OWNER TO "postgres";

--
-- TOC entry 231 (class 1259 OID 16451)
-- Name: autoorders_tcs; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."autoorders_tcs" AS
 SELECT "intcs"."quantity",
    "intcs"."direction",
    "intcs"."account_id",
    "intcs"."order_type",
    "intcs"."order_id",
    "intcs"."instrument_id",
    "intcs"."last_upd",
    "intcs"."comment",
    "intcs"."code",
    "outtcs"."order_id" AS "order_id_out",
    "outtcs"."execution_report_status",
    "outtcs"."lots_requested",
    "outtcs"."lots_executed",
    COALESCE(("intcs"."quantity" - "outtcs"."lots_requested"), "intcs"."quantity") AS "unconfirmed_amount",
    "outtcs"."message",
    "outtcs"."initial_order_price",
    "outtcs"."executed_order_price",
    "outtcs"."total_order_amount",
    "outtcs"."initial_commission",
    "outtcs"."executed_commission",
    "outtcs"."initial_security_price",
    "outtcs"."initial_order_price_pt"
   FROM ("public"."orders_in_tcs" "intcs"
     LEFT JOIN "public"."orders_out_tcs" "outtcs" ON (("intcs"."order_id" = "outtcs"."order_id_in")));


ALTER VIEW "public"."autoorders_tcs" OWNER TO "postgres";

--
-- TOC entry 232 (class 1259 OID 16456)
-- Name: autoorders_grouped_tcs; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."autoorders_grouped_tcs" AS
 SELECT "code",
    "comment",
    "sum"((COALESCE("lots_executed", (0)::bigint) *
        CASE
            WHEN ("direction" = 1) THEN 1
            ELSE '-1'::integer
        END)) AS "amount",
    "sum"((COALESCE("unconfirmed_amount", (0)::bigint) *
        CASE
            WHEN ("direction" = 1) THEN 1
            ELSE '-1'::integer
        END)) AS "unconfirmed_amount",
    "sum"(((COALESCE("lots_requested", (0)::bigint) - COALESCE("lots_executed", (0)::bigint)) *
        CASE
            WHEN ("direction" = 1) THEN 1
            ELSE '-1'::integer
        END)) AS "amount_pending"
   FROM "public"."autoorders_tcs"
  GROUP BY "code", "comment";


ALTER VIEW "public"."autoorders_grouped_tcs" OWNER TO "postgres";

--
-- TOC entry 233 (class 1259 OID 16461)
-- Name: diffhist_t5; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."diffhist_t5" (
    "index" bigint,
    "code" "text",
    "board" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
);


ALTER TABLE "public"."diffhist_t5" OWNER TO "postgres";

--
-- TOC entry 380 (class 1259 OID 149589)
-- Name: futquotesdiff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."futquotesdiff" (
    "code" character varying(16) NOT NULL,
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."futquotesdiff" OWNER TO "postgres";

--
-- TOC entry 379 (class 1259 OID 149582)
-- Name: secquotesdiff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."secquotesdiff" (
    "code" character varying(16) NOT NULL,
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."secquotesdiff" OWNER TO "postgres";

--
-- TOC entry 383 (class 1259 OID 149608)
-- Name: diffminmax; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."diffminmax" AS
 SELECT "code",
    "board",
    "min"("min") AS "min_5mins",
    "max"("max") AS "max_5mins"
   FROM ( SELECT "diffhist_t5"."code",
            "diffhist_t5"."board",
            "diffhist_t5"."min",
            "diffhist_t5"."max"
           FROM "public"."diffhist_t5"
        UNION ALL
         SELECT "futquotesdiff"."code",
            'SPBFUT'::"text" AS "text",
            "futquotesdiff"."min_5mins",
            "futquotesdiff"."max_5mins"
           FROM "public"."futquotesdiff"
        UNION ALL
         SELECT "secquotesdiff"."code",
            'TQBR'::"text" AS "text",
            "secquotesdiff"."min_5mins",
            "secquotesdiff"."max_5mins"
           FROM "public"."secquotesdiff") "t"
  WHERE (("min" IS NOT NULL) AND ("max" IS NOT NULL))
  GROUP BY "code", "board";


ALTER VIEW "public"."diffminmax" OWNER TO "postgres";

--
-- TOC entry 387 (class 1259 OID 149651)
-- Name: orders_my; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."orders_my" (
    "id" integer NOT NULL,
    "activate_id" integer,
    "state" integer,
    "quantity" integer,
    "comment" character varying(128),
    "remains" integer,
    "stop_loss" double precision,
    "take_profit" double precision,
    "parent_id" integer,
    "barrier" double precision,
    "max_amount" integer,
    "pause" double precision,
    "code" character varying(32),
    "direction" integer,
    "pending_conf" integer,
    "pending_unconf" integer,
    "end_time" timestamp with time zone,
    "start_time" timestamp with time zone,
    "provider" character varying(8),
    "order_type" character varying(8),
    "barrier_bound" double precision
);


ALTER TABLE "public"."orders_my" OWNER TO "postgres";

--
-- TOC entry 392 (class 1259 OID 149696)
-- Name: allquotes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."allquotes" AS
 SELECT "allquotes"."code",
    "allquotes"."market",
    "allquotes"."bid",
    "allquotes"."bidamount",
    "allquotes"."ask",
    "allquotes"."askamount",
    "allquotes"."mid",
    "ord"."id",
    "ord"."activate_id",
    "ord"."state",
    "ord"."quantity",
    "ord"."comment",
    "ord"."remains",
    "ord"."stop_loss",
    "ord"."take_profit",
    "ord"."parent_id",
    "ord"."barrier",
    "ord"."max_amount",
    "ord"."pause",
    "ord"."direction",
    COALESCE(("executed"."amount")::integer, 0) AS "amount",
    COALESCE(("executed"."unconfirmed_amount")::integer, 0) AS "unconfirmed_amount",
    COALESCE(("executed"."amount_pending")::integer, 0) AS "amount_pending",
    "ord"."start_time",
    "ord"."end_time",
    "ord"."provider",
    "minmax"."min_5mins",
    "minmax"."max_5mins",
    "ord"."order_type",
    "ord"."barrier_bound"
   FROM ((("public"."allquotes_mini" "allquotes"
     LEFT JOIN ( SELECT "orders_my"."id",
            "orders_my"."activate_id",
            "orders_my"."state",
            "orders_my"."quantity",
            "orders_my"."comment",
            "orders_my"."remains",
            "orders_my"."stop_loss",
            "orders_my"."take_profit",
            "orders_my"."parent_id",
            "orders_my"."barrier",
            "orders_my"."max_amount",
            "orders_my"."pause",
            "orders_my"."code",
            "orders_my"."direction",
            "orders_my"."start_time",
            "orders_my"."end_time",
            "orders_my"."provider",
            "orders_my"."order_type",
            "orders_my"."barrier_bound"
           FROM "public"."orders_my") "ord" ON ((("allquotes"."code")::"text" = ("ord"."code")::"text")))
     LEFT JOIN ( SELECT "autoorders_grouped"."code",
            "autoorders_grouped"."comment",
            "autoorders_grouped"."amount",
            "autoorders_grouped"."unconfirmed_amount",
            "autoorders_grouped"."amount_pending",
            NULL::"text" AS "provider"
           FROM "public"."autoorders_grouped"
        UNION ALL
         SELECT "autoorders_grouped_tcs"."code",
            "autoorders_grouped_tcs"."comment",
            "autoorders_grouped_tcs"."amount",
            "autoorders_grouped_tcs"."unconfirmed_amount",
            "autoorders_grouped_tcs"."amount_pending",
            'tcs'::"text" AS "provider"
           FROM "public"."autoorders_grouped_tcs") "executed" ON ((("executed"."code" = ("ord"."code")::"text") AND ("concat"(("ord"."comment")::"text", "ord"."id") = "executed"."comment") AND ((COALESCE("ord"."provider", ''::character varying))::"text" = COALESCE("executed"."provider", ''::"text")))))
     LEFT JOIN ( SELECT "diffminmax"."code",
            "diffminmax"."min_5mins",
            "diffminmax"."max_5mins"
           FROM "public"."diffminmax") "minmax" ON ((("allquotes"."code")::"text" = "minmax"."code")));


ALTER VIEW "public"."allquotes" OWNER TO "postgres";

--
-- TOC entry 394 (class 1259 OID 149708)
-- Name: pos_collat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."pos_collat" (
    "instrument" character varying(32),
    "view" character varying(8),
    "type" character varying(8),
    "pos" bigint,
    "collateral" double precision,
    "account" character varying(32),
    "code" character varying(16),
    "volume" double precision,
    "dlong" double precision,
    "dshort" double precision
);


ALTER TABLE "public"."pos_collat" OWNER TO "postgres";

--
-- TOC entry 397 (class 1259 OID 149723)
-- Name: pos_money; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."pos_money" (
    "money_prev" double precision,
    "money" double precision,
    "pos_current" double precision,
    "pos_plan" double precision,
    "pnl" double precision,
    "pnl_prev" double precision,
    "fees" double precision,
    "firm" character varying(16),
    "account" character varying(16),
    "type" character varying(16)
);


ALTER TABLE "public"."pos_money" OWNER TO "postgres";

--
-- TOC entry 398 (class 1259 OID 149726)
-- Name: money; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."money" AS
 SELECT "pos_money"."firm" AS "board",
    "pos_money"."pos_plan" AS "money"
   FROM "public"."pos_money"
UNION ALL
 SELECT 'TQBR'::character varying AS "board",
    ("sum"("pos_collat"."volume") - "sum"(
        CASE
            WHEN (("pos_collat"."code")::"text" = 'SUR'::"text") THEN (0)::double precision
            ELSE "pos_collat"."collateral"
        END)) AS "money"
   FROM "public"."pos_collat";


ALTER VIEW "public"."money" OWNER TO "postgres";

--
-- TOC entry 399 (class 1259 OID 149731)
-- Name: allquotes_collat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."allquotes_collat" AS
 SELECT "quotes"."code",
    "quotes"."market",
    "quotes"."bid",
    "quotes"."bidamount",
    "quotes"."ask",
    "quotes"."askamount",
    "quotes"."mid",
    "quotes"."lot",
    "quotes"."dlong",
    "quotes"."dshort",
    "money"."money",
    ("money"."money" / (("quotes"."bid" * ("quotes"."lot")::double precision) * COALESCE("quotes"."dlong", (1)::double precision))) AS "long_avail",
    ("money"."money" / (("quotes"."bid" * ("quotes"."lot")::double precision) * COALESCE("quotes"."dshort", (1)::double precision))) AS "short_avail"
   FROM (( SELECT "futquotes"."code",
            'SPBFUT'::"text" AS "market",
            "futquotes"."bid",
            "futquotes"."bidamount",
            "futquotes"."ask",
            "futquotes"."askamount",
            (("futquotes"."bid" + "futquotes"."ask") / (2)::double precision) AS "mid",
            1 AS "lot",
            ("futquotes"."collateral" / "futquotes"."ask") AS "dlong",
            ("futquotes"."collateral" / "futquotes"."ask") AS "dshort"
           FROM "public"."futquotes"
          WHERE ((("futquotes"."status")::integer = 1) AND ("futquotes"."bidamount" > (0)::double precision) AND ("futquotes"."askamount" > (0)::double precision))
        UNION ALL
         SELECT "secquotes"."code",
            'TQBR'::"text" AS "market",
            "secquotes"."bid",
            "secquotes"."bidamount",
            "secquotes"."ask",
            "secquotes"."askamount",
            (("secquotes"."bid" + "secquotes"."ask") / (2)::double precision) AS "mid",
            "secquotes"."lot",
            "pos_collat"."dlong",
            "pos_collat"."dshort"
           FROM ("public"."secquotes"
             LEFT JOIN "public"."pos_collat" ON ((("secquotes"."code")::"text" = ("pos_collat"."code")::"text")))
          WHERE (("secquotes"."bidamount" > (0)::double precision) AND ("secquotes"."askamount" > (0)::double precision) AND (("secquotes"."session")::integer = 1))) "quotes"
     LEFT JOIN "public"."money" ON (("quotes"."market" = ("money"."board")::"text")));


ALTER VIEW "public"."allquotes_collat" OWNER TO "postgres";

--
-- TOC entry 234 (class 1259 OID 16507)
-- Name: analytics_beta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."analytics_beta" (
    "index" bigint,
    "sec" "text",
    "base_asset" "text",
    "beta" double precision,
    "r2" double precision,
    "corr" double precision
);


ALTER TABLE "public"."analytics_beta" OWNER TO "postgres";

--
-- TOC entry 235 (class 1259 OID 16512)
-- Name: analytics_future; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."analytics_future" (
    "index" bigint,
    "ds" timestamp without time zone,
    "yhat_lower" double precision,
    "yhat_upper" double precision,
    "yhat" double precision,
    "sigma" double precision,
    "trend_abs" double precision,
    "trend_rel_pct" double precision,
    "sec" "text"
);


ALTER TABLE "public"."analytics_future" OWNER TO "postgres";

--
-- TOC entry 236 (class 1259 OID 16517)
-- Name: analytics_past; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."analytics_past" (
    "index" bigint,
    "additive_terms" double precision,
    "wd" integer,
    "dt" time without time zone,
    "additive_terms_prct" double precision,
    "sec" "text"
);


ALTER TABLE "public"."analytics_past" OWNER TO "postgres";

--
-- TOC entry 403 (class 1259 OID 149754)
-- Name: deals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."deals" (
    "deal_id" bigint NOT NULL,
    "order_id" bigint NOT NULL,
    "time" time without time zone,
    "bs" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "comment" character varying(64),
    "broker_fees" double precision,
    "tradedate" "date" NOT NULL,
    "class_code" character varying(32)
);


ALTER TABLE "public"."deals" OWNER TO "postgres";

--
-- TOC entry 382 (class 1259 OID 149602)
-- Name: deals_ba; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."deals_ba" (
    "code" character varying(16) NOT NULL,
    "bid" bigint,
    "price" double precision NOT NULL,
    "ask" bigint,
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."deals_ba" OWNER TO "postgres";

--
-- TOC entry 237 (class 1259 OID 16528)
-- Name: deals_ba_hist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_ba_hist" (
    "code" character varying(16) NOT NULL,
    "price" double precision NOT NULL,
    "last_upd" timestamp with time zone NOT NULL,
    "bid" bigint,
    "ask" bigint,
    "updated_at" timestamp with time zone,
    "bidt1" bigint,
    "askt1" bigint,
    "updated_at_t1" timestamp with time zone,
    "dbid" bigint,
    "dask" bigint
);


ALTER TABLE "public"."deals_ba_hist" OWNER TO "postgres";

--
-- TOC entry 238 (class 1259 OID 16531)
-- Name: deals_ba_t1; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_ba_t1" (
    "code" character varying(16),
    "bid" bigint,
    "price" double precision,
    "ask" bigint,
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."deals_ba_t1" OWNER TO "postgres";

--
-- TOC entry 385 (class 1259 OID 149632)
-- Name: deals_ba_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."deals_ba_view" AS
 SELECT COALESCE("deals_ba"."code", "deals_ba_t1"."code") AS "code",
    COALESCE("deals_ba"."price", "deals_ba_t1"."price") AS "price",
    "now"() AS "last_upd",
    "deals_ba"."bid",
    "deals_ba"."ask",
    "deals_ba"."updated_at",
    "deals_ba_t1"."bid" AS "bidt1",
    "deals_ba_t1"."ask" AS "askt1",
    "deals_ba_t1"."updated_at" AS "updated_at_t1",
    ("deals_ba"."bid" - "deals_ba_t1"."bid") AS "dbid",
    ("deals_ba"."ask" - "deals_ba_t1"."ask") AS "dask"
   FROM ("public"."deals_ba"
     FULL JOIN "public"."deals_ba_t1" ON ((("deals_ba"."price" = "deals_ba_t1"."price") AND (("deals_ba"."code")::"text" = ("deals_ba_t1"."code")::"text"))));


ALTER VIEW "public"."deals_ba_view" OWNER TO "postgres";

--
-- TOC entry 239 (class 1259 OID 16539)
-- Name: deals_imp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_imp" (
    "deal_id" numeric(20,0) NOT NULL,
    "tradedate" "date" NOT NULL,
    "time" time without time zone,
    "time_msc" integer,
    "period" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "bs" character varying(16),
    "open_interest" integer
);


ALTER TABLE "public"."deals_imp" OWNER TO "postgres";

--
-- TOC entry 240 (class 1259 OID 16542)
-- Name: deals_imp_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_imp_arch" (
    "deal_id" numeric(20,0) NOT NULL,
    "tradedate" "date" NOT NULL,
    "time" time without time zone,
    "time_msc" integer,
    "period" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "bs" character varying(16),
    "open_interest" integer
);


ALTER TABLE "public"."deals_imp_arch" OWNER TO "postgres";

--
-- TOC entry 415 (class 1259 OID 4418815)
-- Name: deals_imp_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_imp_t" (
    "datetime" timestamp without time zone NOT NULL,
    "code" character varying(32) NOT NULL,
    "price" double precision NOT NULL,
    "net_amount" numeric,
    "total_amount" numeric,
    "avg_open_interest" numeric
);


ALTER TABLE "public"."deals_imp_t" OWNER TO "postgres";

--
-- TOC entry 241 (class 1259 OID 16545)
-- Name: deals_myhist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."deals_myhist" (
    "deal_id" bigint NOT NULL,
    "order_id" bigint,
    "time" time without time zone,
    "bs" character varying(16),
    "code" character varying(32),
    "price" double precision,
    "amount" bigint,
    "volume" double precision,
    "comment" character varying(64),
    "broker_fees" double precision,
    "tradedate" "date" NOT NULL,
    "class_code" character varying(32)
);


ALTER TABLE "public"."deals_myhist" OWNER TO "postgres";

--
-- TOC entry 242 (class 1259 OID 16548)
-- Name: df_all_candles_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_candles_t" (
    "open" double precision NOT NULL,
    "high" double precision NOT NULL,
    "low" double precision NOT NULL,
    "close" double precision NOT NULL,
    "volume" integer NOT NULL,
    "security" character varying(64) NOT NULL,
    "class_code" character varying(64),
    "datetime" timestamp with time zone NOT NULL
);


ALTER TABLE "public"."df_all_candles_t" OWNER TO "postgres";

--
-- TOC entry 243 (class 1259 OID 16551)
-- Name: df_all_candles_t_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_candles_t_arch" (
    "open" double precision NOT NULL,
    "high" double precision NOT NULL,
    "low" double precision NOT NULL,
    "close" double precision NOT NULL,
    "volume" integer NOT NULL,
    "security" character varying(64) NOT NULL,
    "class_code" character varying(64),
    "datetime" timestamp with time zone NOT NULL
);


ALTER TABLE "public"."df_all_candles_t_arch" OWNER TO "postgres";

--
-- TOC entry 244 (class 1259 OID 16554)
-- Name: df_all_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_levels" (
    "index" bigint,
    "code" "text",
    "name" "text",
    "start" double precision,
    "end" double precision,
    "logic" bigint,
    "std" double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE "public"."df_all_levels" OWNER TO "postgres";

--
-- TOC entry 281 (class 1259 OID 34149)
-- Name: df_all_orderbook_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_orderbook_arch" (
    "price" "text",
    "quantity" bigint,
    "ba" "text",
    "datetime" timestamp with time zone,
    "code" "text",
    "abnormal" boolean,
    "limit" double precision
);


ALTER TABLE "public"."df_all_orderbook_arch" OWNER TO "postgres";

--
-- TOC entry 277 (class 1259 OID 33977)
-- Name: df_all_orderbook_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_orderbook_t" (
    "price" "text",
    "quantity" bigint,
    "ba" "text",
    "datetime" timestamp with time zone,
    "code" "text",
    "abnormal" boolean,
    "limit" double precision
);


ALTER TABLE "public"."df_all_orderbook_t" OWNER TO "postgres";

--
-- TOC entry 245 (class 1259 OID 16559)
-- Name: df_all_volumes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_all_volumes" (
    "index" bigint,
    "price" double precision,
    "volume" double precision,
    "code" "text"
);


ALTER TABLE "public"."df_all_volumes" OWNER TO "postgres";

--
-- TOC entry 246 (class 1259 OID 16564)
-- Name: df_bollinger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_bollinger" (
    "index" bigint,
    "security" "text",
    "class_code" "text",
    "mean" double precision,
    "std" double precision,
    "count" bigint,
    "prct" double precision,
    "up" double precision,
    "down" double precision
);


ALTER TABLE "public"."df_bollinger" OWNER TO "postgres";

--
-- TOC entry 247 (class 1259 OID 16569)
-- Name: df_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_levels" (
    "index" bigint,
    "price" double precision,
    "volume" double precision,
    "std" double precision,
    "sec" "text",
    "min_start" double precision,
    "max_start" double precision,
    "end" double precision,
    "sl" double precision,
    "mid" double precision,
    "down" "text",
    "prev_end" double precision,
    "next_sl" double precision,
    "implied_prob" double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE "public"."df_levels" OWNER TO "postgres";

--
-- TOC entry 248 (class 1259 OID 16574)
-- Name: df_monitor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_monitor" (
    "index" bigint,
    "code" "text",
    "old_state" "text",
    "old_price" double precision,
    "old_start" double precision,
    "old_end" double precision,
    "new_state" "text",
    "new_price" double precision,
    "new_start" double precision,
    "new_end" double precision,
    "std" double precision,
    "old_timestamp" timestamp with time zone,
    "new_timestamp" timestamp with time zone
);


ALTER TABLE "public"."df_monitor" OWNER TO "postgres";

--
-- TOC entry 272 (class 1259 OID 25630)
-- Name: df_volumes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."df_volumes" (
    "security" character varying(64) NOT NULL,
    "class_code" character varying(64),
    "tm" timestamp without time zone NOT NULL,
    "points_num" bigint,
    "volume_std" numeric,
    "volume_std_10" numeric,
    "volume_avg" bigint,
    "volume_avg_10" numeric,
    "money_volume_avg" double precision,
    "money_volume_avg_10" double precision,
    "diff_mean" double precision,
    "diff_mean_10" double precision,
    "diff_std" double precision,
    "diff_std_10" double precision,
    "diff_prct_mean" double precision,
    "diff_prct_mean_10" double precision,
    "diff_prct_std" double precision,
    "diff_prct_std_10" double precision,
    "cnt_days" bigint,
    "max_dt" "date",
    "max_datetime" timestamp with time zone,
    "close" double precision,
    "volume_last" integer,
    "money_volume_last" double precision
);


ALTER TABLE "public"."df_volumes" OWNER TO "postgres";

--
-- TOC entry 388 (class 1259 OID 149657)
-- Name: diffhist_t1510; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."diffhist_t1510" (
    "index" bigint,
    "code" "text",
    "board" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "min_datetime" timestamp with time zone,
    "max_datetime" timestamp with time zone
);


ALTER TABLE "public"."diffhist_t1510" OWNER TO "postgres";

--
-- TOC entry 249 (class 1259 OID 16589)
-- Name: futquotesdiffhist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."futquotesdiffhist" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."futquotesdiffhist" OWNER TO "postgres";

--
-- TOC entry 250 (class 1259 OID 16592)
-- Name: secquotesdiffhist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."secquotesdiffhist" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."secquotesdiffhist" OWNER TO "postgres";

--
-- TOC entry 251 (class 1259 OID 16595)
-- Name: diffhistview; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."diffhistview" AS
 SELECT "secquotesdiffhist"."code",
    'TQBR'::"text" AS "board",
    "min"((("secquotesdiffhist"."bid" + "secquotesdiffhist"."ask") / (2)::double precision)) AS "min",
    "max"((("secquotesdiffhist"."bid" + "secquotesdiffhist"."ask") / (2)::double precision)) AS "max",
    "sum"("secquotesdiffhist"."volume_inc") AS "volume",
    "count"(*) AS "count"
   FROM "public"."secquotesdiffhist"
  WHERE ("secquotesdiffhist"."last_upd" > ("now"() - '00:01:00'::interval))
  GROUP BY "secquotesdiffhist"."code"
 HAVING ("min"("secquotesdiffhist"."bid") > (0)::double precision)
UNION ALL
 SELECT "futquotesdiffhist"."code",
    'SPBFUT'::"text" AS "board",
    "min"((("futquotesdiffhist"."bid" + "futquotesdiffhist"."ask") / (2)::double precision)) AS "min",
    "max"((("futquotesdiffhist"."bid" + "futquotesdiffhist"."ask") / (2)::double precision)) AS "max",
    "sum"("futquotesdiffhist"."volume_inc") AS "volume",
    "count"(*) AS "count"
   FROM "public"."futquotesdiffhist"
  WHERE ("futquotesdiffhist"."last_upd" > ("now"() - '00:01:00'::interval))
  GROUP BY "futquotesdiffhist"."code"
 HAVING ("min"("futquotesdiffhist"."bid") > (0)::double precision);


ALTER VIEW "public"."diffhistview" OWNER TO "postgres";

--
-- TOC entry 252 (class 1259 OID 16600)
-- Name: diffhistview_5; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."diffhistview_5" AS
 SELECT "secquotesdiffhist"."code",
    'TQBR'::"text" AS "board",
    "min"("secquotesdiffhist"."ask") AS "min",
    "max"("secquotesdiffhist"."bid") AS "max",
    "avg"((("secquotesdiffhist"."bid" + "secquotesdiffhist"."ask") / (2)::double precision)) AS "mean",
    "sum"("secquotesdiffhist"."volume_inc") AS "volume",
    "count"(*) AS "count",
    "min"("secquotesdiffhist"."last_upd") AS "min_datetime",
    "max"("secquotesdiffhist"."last_upd") AS "max_datetime"
   FROM "public"."secquotesdiffhist"
  WHERE (("secquotesdiffhist"."last_upd" > ("now"() - '00:05:00'::interval)) AND ("secquotesdiffhist"."bid" > (0)::double precision))
  GROUP BY "secquotesdiffhist"."code"
 HAVING ("min"("secquotesdiffhist"."bid") > (0)::double precision)
UNION ALL
 SELECT "futquotesdiffhist"."code",
    'SPBFUT'::"text" AS "board",
    "min"("futquotesdiffhist"."ask") AS "min",
    "max"("futquotesdiffhist"."bid") AS "max",
    "avg"((("futquotesdiffhist"."bid" + "futquotesdiffhist"."ask") / (2)::double precision)) AS "mean",
    "sum"("futquotesdiffhist"."volume_inc") AS "volume",
    "count"(*) AS "count",
    "min"("futquotesdiffhist"."last_upd") AS "min_datetime",
    "max"("futquotesdiffhist"."last_upd") AS "max_datetime"
   FROM "public"."futquotesdiffhist"
  WHERE (("futquotesdiffhist"."last_upd" > ("now"() - '00:05:00'::interval)) AND ("futquotesdiffhist"."bid" > (0)::double precision))
  GROUP BY "futquotesdiffhist"."code"
 HAVING ("min"("futquotesdiffhist"."bid") > (0)::double precision);


ALTER VIEW "public"."diffhistview_5" OWNER TO "postgres";

--
-- TOC entry 253 (class 1259 OID 16605)
-- Name: diffhistview_t1510; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."diffhistview_t1510" AS
 SELECT "security" AS "code",
    "class_code" AS "board",
    "min"("low") AS "min",
    "max"("high") AS "max",
    "avg"("close") AS "mean",
    "sum"("volume") AS "volume",
    "count"(*) AS "count",
    "min"("datetime") AS "min_datetime",
    "max"("datetime") AS "max_datetime"
   FROM "public"."df_all_candles_t"
  WHERE ((("now"() - '00:05:00'::interval) > "datetime") AND ("datetime" > ("now"() - '00:15:00'::interval)))
  GROUP BY "security", "class_code"
 HAVING ("min"("low") > (0)::double precision);


ALTER VIEW "public"."diffhistview_t1510" OWNER TO "postgres";

--
-- TOC entry 254 (class 1259 OID 16610)
-- Name: diffhistview_t5; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."diffhistview_t5" AS
 SELECT "security" AS "code",
    "class_code" AS "board",
    "min"("low") AS "min",
    "max"("high") AS "max",
    "avg"("close") AS "mean",
    "sum"("volume") AS "volume",
    "count"(*) AS "count",
    "min"("datetime") AS "min_datetime",
    "max"("datetime") AS "max_datetime"
   FROM "public"."df_all_candles_t"
  WHERE (("now"() - '00:05:00'::interval) <= "datetime")
  GROUP BY "security", "class_code"
 HAVING ("min"("low") > (0)::double precision);


ALTER VIEW "public"."diffhistview_t5" OWNER TO "postgres";

--
-- TOC entry 255 (class 1259 OID 16615)
-- Name: event_news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."event_news" (
    "code" character varying(32) NOT NULL,
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(32) NOT NULL,
    "news_time" timestamp with time zone NOT NULL,
    "keyword" character varying(32),
    "msg" "text"
);


ALTER TABLE "public"."event_news" OWNER TO "postgres";

--
-- TOC entry 256 (class 1259 OID 16620)
-- Name: events_jumps_hist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."events_jumps_hist" (
    "index" bigint,
    "code" "text",
    "min" double precision,
    "max" double precision,
    "mean" double precision,
    "volume" bigint,
    "count" bigint,
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "process_time" timestamp with time zone,
    "jump_prct" double precision,
    "out_prct" double precision,
    "volume_peak" double precision,
    "out_std" double precision
);


ALTER TABLE "public"."events_jumps_hist" OWNER TO "postgres";

--
-- TOC entry 381 (class 1259 OID 149596)
-- Name: func_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."func_stats" (
    "name" character varying(64) NOT NULL,
    "num" bigint,
    "avg" double precision,
    "min" double precision,
    "max" double precision,
    "stdev" double precision,
    "last" double precision,
    "last_invoke" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."func_stats" OWNER TO "postgres";

--
-- TOC entry 276 (class 1259 OID 33917)
-- Name: futprefix; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."futprefix" (
    "ticker" character varying(8) NOT NULL,
    "futprefix" character varying(4) NOT NULL
);


ALTER TABLE "public"."futprefix" OWNER TO "postgres";

--
-- TOC entry 368 (class 1259 OID 78542)
-- Name: futquotesdiffhist_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."futquotesdiffhist_arch" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."futquotesdiffhist_arch" OWNER TO "postgres";

--
-- TOC entry 257 (class 1259 OID 16625)
-- Name: futquoteshist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."futquoteshist" (
    "fullid" character varying(128),
    "code" character varying(16),
    "status" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "collateral" double precision,
    "minprice" double precision,
    "maxprice" double precision,
    "openinterest" double precision,
    "volume" double precision,
    "tillmaturity" integer,
    "maturitydate" character varying(16),
    "tradedate" character varying(12),
    "closeprice" double precision,
    "prctchange" double precision,
    "instrumentid" character varying(32),
    "lot" integer,
    "prec" integer,
    "pricestep" double precision,
    "lastdealqty" bigint,
    "lastdealvol" double precision,
    "pricestepcur" double precision,
    "updated_at" timestamp with time zone,
    "snaptimestamp" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."futquoteshist" OWNER TO "postgres";

--
-- TOC entry 393 (class 1259 OID 149701)
-- Name: jump_events; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."jump_events" AS
 SELECT "dh"."code",
    "dh"."min",
    "dh"."max",
    "dh"."mean",
    "dh"."volume",
    "dh"."count",
    "fq"."bid",
    "fq"."bidamount",
    "fq"."ask",
    "fq"."askamount",
    "fq"."volume_inc",
    "fq"."bid_inc",
    "fq"."ask_inc",
    "fq"."updated_at",
    "fq"."last_upd",
    "fq"."volume_wa",
    "now"() AS "process_time",
    ((("fq"."bid_inc" + "fq"."ask_inc") / ("fq"."bid" + "fq"."ask")) * (100)::double precision) AS "jump_prct",
        CASE
            WHEN ("fq"."ask" < "dh"."min") THEN ((- (("dh"."min" / "fq"."ask") - (1)::double precision)) * (100)::double precision)
            ELSE ((("fq"."bid" / "dh"."max") - (1)::double precision) * (100)::double precision)
        END AS "out_prct",
    "round"(((("fq"."volume_inc" * (10)::double precision) / ("dh"."volume")::double precision) * "dh"."max")) AS "volume_peak",
        CASE
            WHEN ("fq"."ask" < "dh"."min") THEN (("fq"."ask" - "dh"."min") / ("dh"."max" - "dh"."min"))
            ELSE (("fq"."bid" - "dh"."max") / ("dh"."max" - "dh"."min"))
        END AS "out_std"
   FROM ("public"."diffhist_t1510" "dh"
     JOIN "public"."futquotesdiff" "fq" ON (("dh"."code" = ("fq"."code")::"text")))
  WHERE (("dh"."volume" > 0) AND (("dh"."max" - "dh"."min") > (0)::double precision) AND (((("dh"."volume")::double precision * "dh"."max") / (10)::double precision) < "fq"."volume_inc") AND (("fq"."ask" < "dh"."min") OR ("fq"."bid" > "dh"."max")) AND ("fq"."bid" > (0)::double precision));


ALTER VIEW "public"."jump_events" OWNER TO "postgres";

--
-- TOC entry 406 (class 1259 OID 149924)
-- Name: news_tfidf; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."news_tfidf" (
    "ticker" "text",
    "tfidfsum" double precision,
    "total_daily" bigint,
    "total_with_ticker" bigint,
    "date" "date"
);


ALTER TABLE "public"."news_tfidf" OWNER TO "postgres";

--
-- TOC entry 258 (class 1259 OID 16634)
-- Name: order_discovery; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."order_discovery" (
    "code" character varying(32),
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(32),
    "news_time" timestamp with time zone,
    "min_val" double precision,
    "max_val" double precision,
    "mean_val" double precision,
    "volume" double precision
);


ALTER TABLE "public"."order_discovery" OWNER TO "postgres";

--
-- TOC entry 282 (class 1259 OID 34679)
-- Name: order_dividend; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."order_dividend" (
    "ticker" character varying(16) NOT NULL,
    "divval_gte" double precision,
    "gte_order_id" bigint,
    "divval_lte" double precision,
    "lte_order_id" bigint,
    "is_activated" boolean DEFAULT false,
    "activation_time" timestamp without time zone,
    "dividend" character varying(32)
);


ALTER TABLE "public"."order_dividend" OWNER TO "postgres";

--
-- TOC entry 279 (class 1259 OID 34094)
-- Name: orders_activator_shared_sequence; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "public"."orders_activator_shared_sequence"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."orders_activator_shared_sequence" OWNER TO "postgres";

--
-- TOC entry 259 (class 1259 OID 16637)
-- Name: orders_auto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_auto" (
    "code" character varying(16),
    "market" character varying(16),
    "amount" bigint,
    "limit" double precision,
    "executed" bigint,
    "lastorder" bigint,
    "maxspreadprc" double precision,
    "id" integer NOT NULL,
    "strategy" character varying(16)
);


ALTER TABLE "public"."orders_auto" OWNER TO "postgres";

--
-- TOC entry 260 (class 1259 OID 16640)
-- Name: orders_auto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "public"."orders_auto_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."orders_auto_id_seq" OWNER TO "postgres";

--
-- TOC entry 4406 (class 0 OID 0)
-- Dependencies: 260
-- Name: orders_auto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "public"."orders_auto_id_seq" OWNED BY "public"."orders_auto"."id";


--
-- TOC entry 280 (class 1259 OID 34111)
-- Name: orders_event_activator; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."orders_event_activator" (
    "id" bigint NOT NULL,
    "jumps_id" bigint,
    "news_id" bigint,
    "price_id" bigint,
    "is_activated" boolean DEFAULT false NOT NULL,
    "activation_time" timestamp with time zone
);


ALTER TABLE "public"."orders_event_activator" OWNER TO "postgres";

--
-- TOC entry 389 (class 1259 OID 149663)
-- Name: orders_event_activator_jumps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."orders_event_activator_jumps" (
    "id" bigint DEFAULT "nextval"('"public"."orders_activator_shared_sequence"'::"regclass") NOT NULL,
    "ticker" character varying(16) NOT NULL,
    "start_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "end_date" timestamp with time zone DEFAULT ("now"() + '00:00:01'::interval) NOT NULL,
    "is_activated" boolean DEFAULT false NOT NULL,
    "jump_prct" double precision,
    "out_prct" double precision,
    "volume_peak" double precision,
    "out_std" double precision,
    "activate_time" timestamp with time zone
);


ALTER TABLE "public"."orders_event_activator_jumps" OWNER TO "postgres";

--
-- TOC entry 390 (class 1259 OID 149672)
-- Name: orders_event_activator_news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."orders_event_activator_news" (
    "id" bigint DEFAULT "nextval"('"public"."orders_activator_shared_sequence"'::"regclass") NOT NULL,
    "ticker" character varying(16),
    "keyword" character varying(16),
    "start_date" timestamp with time zone DEFAULT "now"(),
    "end_date" timestamp with time zone DEFAULT ("now"() + '00:00:01'::interval),
    "is_activated" boolean DEFAULT false,
    "activate_time" timestamp with time zone,
    "channel_source" character varying(32) DEFAULT 'markettwits'::character varying
);


ALTER TABLE "public"."orders_event_activator_news" OWNER TO "postgres";

--
-- TOC entry 391 (class 1259 OID 149682)
-- Name: orders_event_activator_price; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."orders_event_activator_price" (
    "id" bigint DEFAULT "nextval"('"public"."orders_activator_shared_sequence"'::"regclass") NOT NULL,
    "ticker" character varying(16) NOT NULL,
    "price_limit" double precision,
    "start_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "end_date" timestamp with time zone DEFAULT ("now"() + '00:00:01'::interval) NOT NULL,
    "is_activated" boolean DEFAULT false NOT NULL,
    "activate_time" timestamp with time zone
);


ALTER TABLE "public"."orders_event_activator_price" OWNER TO "postgres";

--
-- TOC entry 386 (class 1259 OID 149650)
-- Name: orders_my_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "public"."orders_my_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE "public"."orders_my_id_seq" OWNER TO "postgres";

--
-- TOC entry 4407 (class 0 OID 0)
-- Dependencies: 386
-- Name: orders_my_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "public"."orders_my_id_seq" OWNED BY "public"."orders_my"."id";


--
-- TOC entry 395 (class 1259 OID 149713)
-- Name: pos_eq; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."pos_eq" (
    "instrument" character varying(32),
    "pos" bigint,
    "price" double precision,
    "volume" double precision,
    "pnl" double precision,
    "buy" bigint,
    "sell" bigint,
    "tobuy" bigint,
    "tosell" bigint,
    "firm" character varying(32),
    "account" character varying(32),
    "client_id" character varying(32),
    "settlement" character varying(4),
    "code" character varying(16)
);


ALTER TABLE "public"."pos_eq" OWNER TO "postgres";

--
-- TOC entry 396 (class 1259 OID 149718)
-- Name: pos_fut; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE "public"."pos_fut" (
    "code" character varying(16),
    "instrument" character varying(32),
    "maturity" "date",
    "pos" bigint,
    "buy" bigint,
    "sell" bigint,
    "pnl" double precision,
    "price_balance" double precision,
    "firm" character varying(16),
    "account" character varying(16),
    "type" character varying(16)
);


ALTER TABLE "public"."pos_fut" OWNER TO "postgres";

--
-- TOC entry 261 (class 1259 OID 16663)
-- Name: pos_volmult; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."pos_volmult" (
    "code" character varying NOT NULL,
    "multiplier" double precision NOT NULL
);


ALTER TABLE "public"."pos_volmult" OWNER TO "postgres";

--
-- TOC entry 384 (class 1259 OID 149623)
-- Name: quote_bollinger; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."quote_bollinger" AS
 SELECT "q"."code",
    "b"."class_code",
    "q"."quote",
    (("q"."quote" - "b"."mean") / "b"."std") AS "bollinger",
    "b"."count",
    "b"."up",
    "b"."down"
   FROM (( SELECT "futquotesdiff"."code",
            (("futquotesdiff"."bid" + "futquotesdiff"."ask") / (2)::double precision) AS "quote"
           FROM "public"."futquotesdiff"
        UNION ALL
         SELECT "secquotes"."code",
            (("secquotes"."bid" + "secquotes"."ask") / (2)::double precision)
           FROM "public"."secquotes") "q"
     JOIN "public"."df_bollinger" "b" ON ((("q"."code")::"text" = "b"."security")))
  WHERE ("q"."quote" > (0)::double precision)
  ORDER BY (("q"."quote" - "b"."mean") / "b"."std") DESC;


ALTER VIEW "public"."quote_bollinger" OWNER TO "postgres";

--
-- TOC entry 400 (class 1259 OID 149736)
-- Name: united_pos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."united_pos" AS
 SELECT "pos_fut"."code",
    "pos_fut"."pos",
    "pos_fut"."buy",
    "pos_fut"."sell",
    "pos_fut"."pnl",
    "pos_fut"."price_balance",
    (((("pos_fut"."pos")::double precision * "pos_fut"."price_balance") * COALESCE("pos_volmult"."multiplier", (1)::double precision)) + "pos_fut"."pnl") AS "volume",
    "pos_fut"."firm"
   FROM ("public"."pos_fut"
     LEFT JOIN "public"."pos_volmult" ON (("left"(("pos_fut"."code")::"text", 2) = ("pos_volmult"."code")::"text")))
  WHERE ((("abs"("pos_fut"."pos") + "pos_fut"."buy") + "pos_fut"."sell") <> 0)
UNION ALL
 SELECT "pos_eq"."code",
    "pos_eq"."pos",
    "pos_eq"."buy",
    "pos_eq"."sell",
    "pos_eq"."pnl",
    "pos_eq"."price" AS "price_balance",
    ("pos_eq"."volume" + "pos_eq"."pnl") AS "volume",
    'TQBR'::character varying AS "firm"
   FROM "public"."pos_eq"
  WHERE ((("abs"("pos_eq"."pos") + "pos_eq"."buy") + "pos_eq"."sell") <> 0);


ALTER VIEW "public"."united_pos" OWNER TO "postgres";

--
-- TOC entry 401 (class 1259 OID 149741)
-- Name: pos_bollinger; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."pos_bollinger" AS
 SELECT "p"."code",
    "p"."pos",
    "p"."buy",
    "p"."sell",
    "p"."pnl",
    "p"."price_balance",
    "p"."volume",
    "p"."firm",
    "b"."bollinger",
    "b"."count",
    "b"."up",
    "b"."down"
   FROM ("public"."quote_bollinger" "b"
     JOIN "public"."united_pos" "p" ON ((("b"."code")::"text" = ("p"."code")::"text")));


ALTER VIEW "public"."pos_bollinger" OWNER TO "postgres";

--
-- TOC entry 378 (class 1259 OID 149573)
-- Name: potential; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."potential" AS
 SELECT ((("t2"."max" / "t1"."price") - (1)::double precision) * "t1"."leverage") AS "potential",
    "t2"."max",
    "t1"."price",
    "t1"."leverage",
    COALESCE("t1"."code", "t2"."security") AS "code",
    (((("t2"."max" / "t1"."price") - (1)::double precision) * "t1"."leverage") / "af"."sigma") AS "potential_sharp",
    "af"."sigma"
   FROM ((( SELECT "futquotes"."code",
            (("futquotes"."bid" + "futquotes"."ask") / (2)::double precision) AS "price",
            ((("futquotes"."bid" + "futquotes"."ask") / (2)::double precision) / "futquotes"."collateral") AS "leverage"
           FROM "public"."futquotes") "t1"
     FULL JOIN ( SELECT "max"("df_all_candles_t"."close") AS "max",
            "df_all_candles_t"."security"
           FROM "public"."df_all_candles_t"
          WHERE (("df_all_candles_t"."class_code")::"text" = 'SPBFUT'::"text")
          GROUP BY "df_all_candles_t"."security") "t2" ON ((("t1"."code")::"text" = ("t2"."security")::"text")))
     LEFT JOIN "public"."analytics_future" "af" ON (("af"."sec" = (COALESCE("t1"."code", "t2"."security"))::"text")))
  ORDER BY ((("t2"."max" / "t1"."price") - (1)::double precision) * "t1"."leverage") DESC;


ALTER VIEW "public"."potential" OWNER TO "postgres";

--
-- TOC entry 273 (class 1259 OID 25665)
-- Name: public.df_monitor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."public.df_monitor" (
    "level_0" bigint,
    "index" bigint,
    "code" "text",
    "old_state" "text",
    "old_price" double precision,
    "old_start" double precision,
    "old_end" double precision,
    "new_state" "text",
    "new_price" double precision,
    "new_start" double precision,
    "new_end" double precision,
    "std" double precision,
    "old_timestamp" timestamp with time zone,
    "new_timestamp" timestamp with time zone
);


ALTER TABLE "public"."public.df_monitor" OWNER TO "postgres";

--
-- TOC entry 262 (class 1259 OID 16687)
-- Name: report_big_deals; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_big_deals" AS
 SELECT "sum"(((
        CASE
            WHEN (("bs")::"text" = 'BUY'::"text") THEN 1
            WHEN (("bs")::"text" = 'SELL'::"text") THEN '-1'::integer
            ELSE 0
        END)::double precision * "volume")) AS "net_amount",
    ("tradedate" + "time") AS "datetime",
    "code",
    "max"("price") AS "max_price",
    "min"("price") AS "min_price",
    (((200)::double precision * ("max"("price") - "min"("price"))) / ("max"("price") + "min"("price"))) AS "shift_abs",
    ("max"("open_interest") - "min"("open_interest")) AS "open_interest_diff"
   FROM "public"."deals_imp"
  GROUP BY ("tradedate" + "time"), "code"
 HAVING ("abs"("sum"(((
        CASE
            WHEN (("bs")::"text" = 'BUY'::"text") THEN 1
            WHEN (("bs")::"text" = 'SELL'::"text") THEN '-1'::integer
            ELSE 0
        END)::double precision * "volume"))) > (20000000)::double precision)
  ORDER BY "code", ("tradedate" + "time") DESC;


ALTER VIEW "public"."report_big_deals" OWNER TO "postgres";

--
-- TOC entry 271 (class 1259 OID 17415)
-- Name: report_daily_patterns; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_daily_patterns" AS
 SELECT "close",
    ("close" - "lag"("close", 1) OVER (PARTITION BY "security" ORDER BY "datetime")) AS "diff",
    "abs"(("close" - "lag"("close", 1) OVER (PARTITION BY "security" ORDER BY "datetime"))) AS "abs_diff",
    "volume",
    "security",
    "datetime",
    (CURRENT_DATE + ("datetime")::time without time zone) AS "tm",
    (EXTRACT(dow FROM "datetime"))::"text" AS "wd",
    "class_code"
   FROM "public"."df_all_candles_t"
  WHERE (EXTRACT(dow FROM "datetime") <> ALL (ARRAY[(0)::numeric, (6)::numeric]));


ALTER VIEW "public"."report_daily_patterns" OWNER TO "postgres";

--
-- TOC entry 370 (class 1259 OID 138288)
-- Name: report_dbsize; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_dbsize" AS
 SELECT "table_name",
    "pg_size_pretty"("pg_total_relation_size"(("quote_ident"(("table_name")::"text"))::"regclass")) AS "pg_size_pretty",
    "pg_total_relation_size"(("quote_ident"(("table_name")::"text"))::"regclass") AS "pg_total_relation_size"
   FROM "information_schema"."tables"
  WHERE (("table_schema")::"name" = 'public'::"name")
  ORDER BY ("pg_total_relation_size"(("quote_ident"(("table_name")::"text"))::"regclass")) DESC;


ALTER VIEW "public"."report_dbsize" OWNER TO "postgres";

--
-- TOC entry 263 (class 1259 OID 16692)
-- Name: report_deal_imp; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_deal_imp" AS
 SELECT DISTINCT ON ("price", "code", "datetime") "datetime",
    "code",
    "price",
    "net_amount",
    "total_amount",
    "avg_open_interest"
   FROM ( SELECT "deals_imp_t"."datetime",
            "deals_imp_t"."code",
            "deals_imp_t"."price",
            "deals_imp_t"."net_amount",
            "deals_imp_t"."total_amount",
            "deals_imp_t"."avg_open_interest"
           FROM "public"."deals_imp_t"
        UNION ALL
         SELECT ("deals_imp"."tradedate" + "deals_imp"."time") AS "datetime",
            "deals_imp"."code",
            "deals_imp"."price",
            "sum"((
                CASE
                    WHEN (("deals_imp"."bs")::"text" = 'BUY'::"text") THEN 1
                    WHEN (("deals_imp"."bs")::"text" = 'SELL'::"text") THEN '-1'::integer
                    ELSE 0
                END * "deals_imp"."amount")) AS "net_amount",
            "sum"("deals_imp"."amount") AS "total_amount",
            "avg"("deals_imp"."open_interest") AS "avg_open_interest"
           FROM "public"."deals_imp"
          WHERE ((( SELECT "count"(*) AS "count"
                   FROM "public"."deals_imp_t") = 0) OR (("deals_imp"."tradedate" + "deals_imp"."time") > ( SELECT "min"("subquery"."max_datetime") AS "min"
                   FROM ( SELECT "deals_imp_t"."code",
                            "max"("deals_imp_t"."datetime") AS "max_datetime"
                           FROM "public"."deals_imp_t"
                          GROUP BY "deals_imp_t"."code") "subquery")))
          GROUP BY "deals_imp"."code", ("deals_imp"."tradedate" + "deals_imp"."time"), "deals_imp"."price") "combined"
  ORDER BY "price", "code", "datetime";


ALTER VIEW "public"."report_deal_imp" OWNER TO "postgres";

--
-- TOC entry 371 (class 1259 OID 138296)
-- Name: report_deal_imp_arch; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_deal_imp_arch" AS
 SELECT ("tradedate" + "time") AS "datetime",
    "code",
    "price",
    "sum"((
        CASE
            WHEN (("bs")::"text" = 'BUY'::"text") THEN 1
            WHEN (("bs")::"text" = 'SELL'::"text") THEN '-1'::integer
            ELSE 0
        END * "amount")) AS "net_amount",
    "sum"("amount") AS "total_amount",
    "avg"("open_interest") AS "avg_open_interest"
   FROM "public"."deals_imp_arch"
  GROUP BY "code", ("tradedate" + "time"), "bs", "price"
  ORDER BY "code", ("tradedate" + "time") DESC;


ALTER VIEW "public"."report_deal_imp_arch" OWNER TO "postgres";

--
-- TOC entry 408 (class 1259 OID 152806)
-- Name: report_deal_imp_arch_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."report_deal_imp_arch_t" (
    "datetime" timestamp without time zone,
    "code" character varying(32),
    "price" double precision,
    "net_amount" numeric,
    "total_amount" numeric,
    "avg_open_interest" numeric
);


ALTER TABLE "public"."report_deal_imp_arch_t" OWNER TO "postgres";

--
-- TOC entry 416 (class 1259 OID 4453541)
-- Name: report_deal_imp_full; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_deal_imp_full" AS
 SELECT ("tradedate" + "time") AS "datetime",
    "code",
    "price",
    "sum"((
        CASE
            WHEN (("bs")::"text" = 'BUY'::"text") THEN 1
            WHEN (("bs")::"text" = 'SELL'::"text") THEN '-1'::integer
            ELSE 0
        END * "amount")) AS "net_amount",
    "sum"("amount") AS "total_amount",
    "avg"("open_interest") AS "avg_open_interest"
   FROM "public"."deals_imp"
  GROUP BY "code", ("tradedate" + "time"), "price"
  ORDER BY "code", ("tradedate" + "time") DESC;


ALTER VIEW "public"."report_deal_imp_full" OWNER TO "postgres";

--
-- TOC entry 377 (class 1259 OID 149568)
-- Name: report_futyield; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_futyield" AS
 SELECT "fq"."code" AS "futcode",
    (("sq"."bid" + "sq"."ask") / (2)::double precision) AS "secprice",
    ((("fq"."bid" + "fq"."ask") / (2)::double precision) / ("fq"."lot")::double precision) AS "futprice",
    "fq"."tillmaturity",
    ((100)::double precision * ("power"(((("fq"."bid" + "fq"."ask") / ("fq"."lot")::double precision) / ("sq"."bid" + "sq"."ask")), ((365 / "fq"."tillmaturity"))::double precision) - (1)::double precision)) AS "yearly_prct",
    (((((((100 * 365) / "fq"."tillmaturity"))::double precision / "power"(((("fq"."bid" + "fq"."ask") / ("fq"."lot")::double precision) / ("sq"."bid" + "sq"."ask")), (((365 / "fq"."tillmaturity") + 1))::double precision)) / ("fq"."bid" + "fq"."ask")) * (2)::double precision) * ("fq"."lot")::double precision) AS "div_rub_adj",
    "sq"."code",
    "fq"."maturitydate",
    "sq"."lot",
    ((100)::double precision * (((("fq"."bid" + "fq"."ask") / ("fq"."lot")::double precision) / ("sq"."bid" + "sq"."ask")) - (1)::double precision)) AS "prct",
    "fp"."ticker",
    "fp"."futprefix"
   FROM (("public"."futquotes" "fq"
     LEFT JOIN "public"."futprefix" "fp" ON (("left"(("fq"."code")::"text", 2) = ("fp"."futprefix")::"text")))
     LEFT JOIN "public"."secquotes" "sq" ON ((("fp"."ticker")::"text" = ("sq"."code")::"text")))
  ORDER BY "fq"."code";


ALTER VIEW "public"."report_futyield" OWNER TO "postgres";

--
-- TOC entry 407 (class 1259 OID 150525)
-- Name: report_minmax; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."report_minmax" (
    "security" character varying(64),
    "date" "date",
    "min_max" double precision,
    "high_low" double precision,
    "min_max_prct" double precision
);


ALTER TABLE "public"."report_minmax" OWNER TO "postgres";

--
-- TOC entry 278 (class 1259 OID 33982)
-- Name: report_plita; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_plita" AS
 SELECT "orders"."price",
    "orders"."quantity",
    "orders"."ba",
    "orders"."datetime",
    "orders"."code",
    "orders"."abnormal",
    "orders"."limit",
    COALESCE("hist"."minutes", (0)::bigint) AS "minutes"
   FROM (("public"."df_all_orderbook_t" "orders"
     JOIN ( SELECT "df_all_orderbook_t"."code",
            "max"("df_all_orderbook_t"."price") AS "price"
           FROM "public"."df_all_orderbook_t"
          WHERE (("df_all_orderbook_t"."abnormal" = true) AND ("df_all_orderbook_t"."ba" = 'bid'::"text"))
          GROUP BY "df_all_orderbook_t"."code"
        UNION ALL
         SELECT "df_all_orderbook_t"."code",
            "min"("df_all_orderbook_t"."price") AS "price"
           FROM "public"."df_all_orderbook_t"
          WHERE (("df_all_orderbook_t"."abnormal" = true) AND ("df_all_orderbook_t"."ba" = 'ask'::"text"))
          GROUP BY "df_all_orderbook_t"."code") "best_ba" ON ((("orders"."code" = "best_ba"."code") AND ("orders"."price" = "best_ba"."price"))))
     LEFT JOIN ( SELECT "df_all_orderbook_arch"."price",
            "df_all_orderbook_arch"."ba",
            "df_all_orderbook_arch"."code",
            "count"(*) AS "minutes"
           FROM "public"."df_all_orderbook_arch"
          WHERE (("df_all_orderbook_arch"."abnormal" = true) AND ("df_all_orderbook_arch"."datetime" > ("now"() - '01:00:00'::interval)))
          GROUP BY "df_all_orderbook_arch"."price", "df_all_orderbook_arch"."ba", "df_all_orderbook_arch"."code") "hist" ON ((("orders"."ba" = "hist"."ba") AND ("orders"."code" = "hist"."code") AND ("orders"."price" = "hist"."price"))));


ALTER VIEW "public"."report_plita" OWNER TO "postgres";

--
-- TOC entry 414 (class 1259 OID 1283074)
-- Name: report_plita_tbl; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."report_plita_tbl" (
    "security" character varying(64) NOT NULL,
    "datetime" timestamp with time zone NOT NULL,
    "bid" double precision,
    "close" double precision,
    "q_bid" bigint,
    "ask" double precision,
    "q_ask" bigint
);


ALTER TABLE "public"."report_plita_tbl" OWNER TO "postgres";

--
-- TOC entry 413 (class 1259 OID 1283070)
-- Name: report_process_news; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_process_news" AS
 SELECT ("date_discovery" - "news_time") AS "process_time",
    "code",
    "date_discovery",
    "channel_source",
    "news_time",
    "keyword",
    "msg"
   FROM "public"."event_news"
  ORDER BY "news_time" DESC;


ALTER VIEW "public"."report_process_news" OWNER TO "postgres";

--
-- TOC entry 411 (class 1259 OID 161242)
-- Name: report_tfidf; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_tfidf" AS
 WITH "dates" AS (
         SELECT DISTINCT "news_tfidf"."date"
           FROM "public"."news_tfidf"
          ORDER BY "news_tfidf"."date" DESC
         LIMIT 20
        ), "tickers" AS (
         SELECT DISTINCT "news_tfidf"."ticker"
           FROM "public"."news_tfidf"
          WHERE ("news_tfidf"."date" IN ( SELECT "dates"."date"
                   FROM "dates"))
        ), "news" AS (
         SELECT DISTINCT "news_tfidf"."ticker",
            "news_tfidf"."tfidfsum",
            "news_tfidf"."total_daily",
            "news_tfidf"."total_with_ticker",
            "news_tfidf"."date"
           FROM "public"."news_tfidf"
        ), "full_data" AS (
         SELECT "dates"."date",
            "tickers"."ticker",
            COALESCE("news"."tfidfsum", (0)::double precision) AS "tfidf",
            COALESCE("news"."total_with_ticker", (0)::bigint) AS "total_with_ticker"
           FROM (("dates"
             CROSS JOIN "tickers")
             LEFT JOIN "news" ON ((("tickers"."ticker" = "news"."ticker") AND ("dates"."date" = "news"."date"))))
        )
 SELECT "td"."ticker",
    ((("td"."tfidf_td" / NULLIF("history"."tfidf_mean", (0)::double precision)) - (1)::double precision) * (100)::double precision) AS "tfidf_inc_prct",
    ((("td"."total_td" / NULLIF("history"."total_mean", (0)::numeric)) - (1)::numeric) * (100)::numeric) AS "total_inc_prct",
    "td"."tfidf_td",
    "td"."total_td",
    "history"."tfidf_mean",
    "history"."total_mean",
    "td"."date"
   FROM (( SELECT "full_data"."ticker",
            "avg"("full_data"."tfidf") AS "tfidf_mean",
            "avg"("full_data"."total_with_ticker") AS "total_mean"
           FROM "full_data"
          WHERE ("full_data"."date" <> ( SELECT "max"("dates"."date") AS "max"
                   FROM "dates"))
          GROUP BY "full_data"."ticker") "history"
     FULL JOIN ( SELECT "full_data"."ticker",
            "avg"("full_data"."tfidf") AS "tfidf_td",
            "avg"("full_data"."total_with_ticker") AS "total_td",
            "full_data"."date"
           FROM "full_data"
          WHERE ("full_data"."date" = ( SELECT "max"("dates"."date") AS "max"
                   FROM "dates"))
          GROUP BY "full_data"."ticker", "full_data"."date") "td" ON (("history"."ticker" = "td"."ticker")));


ALTER VIEW "public"."report_tfidf" OWNER TO "postgres";

--
-- TOC entry 274 (class 1259 OID 33892)
-- Name: report_volumes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_volumes" AS
 WITH "cnd" AS (
         SELECT "df_all_candles_t"."open",
            "df_all_candles_t"."high",
            "df_all_candles_t"."low",
            "df_all_candles_t"."close",
            "df_all_candles_t"."volume",
            "df_all_candles_t"."security",
            "df_all_candles_t"."class_code",
            "df_all_candles_t"."datetime"
           FROM "public"."df_all_candles_t"
          WHERE (("date"("df_all_candles_t"."datetime") = CURRENT_DATE) AND (("df_all_candles_t"."class_code")::"text" <> 'TQPI'::"text"))
        ), "last_candles" AS (
         SELECT "cnd_1"."security",
            "max"("cnd_1"."datetime") AS "crnt_time"
           FROM "cnd" "cnd_1"
          GROUP BY "cnd_1"."security"
        ), "current_price" AS (
         SELECT "cnd_1"."security",
            "cnd_1"."close" AS "crnt_close",
            "last_candles"."crnt_time"
           FROM ("cnd" "cnd_1"
             JOIN "last_candles" ON (((("cnd_1"."security")::"text" = ("last_candles"."security")::"text") AND ("cnd_1"."datetime" = "last_candles"."crnt_time"))))
        )
 SELECT "cnd"."security",
    COALESCE("vol"."class_code", "cnd"."class_code") AS "class_code",
    "cnd"."datetime",
    COALESCE("cnd"."volume", 0) AS "volume",
    "cnd"."close",
    "current_price"."crnt_close",
    "vol"."close" AS "prev_close",
    "current_price"."crnt_time",
    COALESCE((("cnd"."volume")::double precision * "cnd"."close"), (0)::double precision) AS "money_volume",
    ("cnd"."close" - "vol"."close") AS "daily_diff",
    ("cnd"."close" - "lag"("cnd"."close", 1) OVER (PARTITION BY "cnd"."security" ORDER BY "cnd"."datetime")) AS "diff",
    "vol"."points_num",
    "vol"."volume_std",
    "vol"."volume_avg",
    "vol"."volume_avg_10",
    "vol"."money_volume_avg",
    "vol"."money_volume_avg_10",
    "vol"."diff_mean",
    "vol"."diff_mean_10",
    "vol"."diff_std",
    "vol"."diff_std_10",
    "vol"."diff_prct_mean",
    "vol"."diff_prct_mean_10",
    "vol"."diff_prct_std",
    "vol"."diff_prct_std_10",
    "vol"."cnt_days",
    "vol"."max_dt",
    "vol"."max_datetime",
    "vol"."volume_last",
    "vol"."money_volume_last"
   FROM (("cnd"
     FULL JOIN "public"."df_volumes" "vol" ON (((("cnd"."security")::"text" = ("vol"."security")::"text") AND ((CURRENT_DATE + ("cnd"."datetime")::time without time zone) = "vol"."tm"))))
     LEFT JOIN "current_price" ON ((("cnd"."security")::"text" = ("current_price"."security")::"text")))
  WHERE ("vol"."tm" <= "current_price"."crnt_time");


ALTER VIEW "public"."report_volumes" OWNER TO "postgres";

--
-- TOC entry 275 (class 1259 OID 33897)
-- Name: report_volumes_agg; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."report_volumes_agg" AS
 SELECT "security",
    "class_code",
    "max"("crnt_time") AS "time",
    "max"("crnt_close") AS "price",
    "max"("prev_close") AS "ytd_price",
    "max"("max_datetime") AS "ytd_time",
    ((("max"("crnt_close") / NULLIF("max"("prev_close"), (0)::double precision)) - (1)::double precision) * (100)::double precision) AS "inc",
    "sum"("money_volume") AS "td_mvolume",
    "sum"("money_volume_last") AS "ytd_mvolume",
    "sum"("money_volume_avg") AS "avg_mvolume",
    ((("sum"("money_volume") / NULLIF("sum"("money_volume_last"), (0)::double precision)) - (1)::double precision) * (100)::double precision) AS "mvolume_inc",
    ((("sum"("money_volume") / NULLIF("sum"("money_volume_avg"), (0)::double precision)) - (1)::double precision) * (100)::double precision) AS "mvolume_inc_avg",
    "sum"("volume") AS "td_volume",
    "sum"("volume_last") AS "ytd_volume",
    "sum"("volume_avg") AS "avg_volume",
    ((("sum"("volume") / NULLIF("sum"("volume_last"), 0)) - 1) * 100) AS "volume_inc",
    (((("sum"("volume"))::numeric / NULLIF("sum"("volume_avg"), (0)::numeric)) - (1)::numeric) * (100)::numeric) AS "volume_inc_avg",
    "avg"("cnt_days") AS "avg",
    "max"("max_dt") AS "max"
   FROM "public"."report_volumes"
  GROUP BY "security", "class_code";


ALTER VIEW "public"."report_volumes_agg" OWNER TO "postgres";

--
-- TOC entry 369 (class 1259 OID 78547)
-- Name: secquotesdiffhist_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."secquotesdiffhist_arch" (
    "code" character varying(16),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "volume" double precision,
    "volume_inc" double precision,
    "bid_inc" double precision,
    "ask_inc" double precision,
    "updated_at" timestamp with time zone,
    "last_upd" timestamp with time zone,
    "volume_wa" double precision,
    "min_5mins" double precision,
    "max_5mins" double precision
);


ALTER TABLE "public"."secquotesdiffhist_arch" OWNER TO "postgres";

--
-- TOC entry 264 (class 1259 OID 16697)
-- Name: secquoteshist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."secquoteshist" (
    "fullid" character varying(128),
    "instrumentid" character varying(32),
    "type" character varying(16),
    "code" character varying(16),
    "tradedate" character varying(12),
    "currency" character varying(8),
    "bid" double precision,
    "bidamount" double precision,
    "ask" double precision,
    "askamount" double precision,
    "lastprice" double precision,
    "volume" double precision,
    "prctchange" double precision,
    "lastdealtime" character varying(32),
    "session" character varying(32),
    "listing" integer,
    "valuedate" character varying(16),
    "isin" character varying(16),
    "timestamp" time with time zone,
    "snaptimestamp" time with time zone DEFAULT "now"(),
    "lot" integer,
    "prec" bigint,
    "pricestep" double precision,
    "lastdealqty" double precision,
    "lastdealvol" double precision,
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."secquoteshist" OWNER TO "postgres";

--
-- TOC entry 265 (class 1259 OID 16701)
-- Name: signal; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."signal" AS
 SELECT "now"() AS "tstz",
    "od"."code",
    "od"."date_discovery",
    "od"."channel_source",
    "od"."news_time",
    "od"."min_val",
    "od"."max_val",
    "od"."mean_val",
    "od"."volume",
    "dhv"."board",
    "dhv"."min",
    "dhv"."max",
    "dhv"."volume" AS "last_volume",
    "dhv"."count"
   FROM ("public"."order_discovery" "od"
     JOIN "public"."diffhistview" "dhv" ON ((("od"."code")::"text" = ("dhv"."code")::"text")))
  WHERE ((("dhv"."max" - "dhv"."min") > ("od"."max_val" - "od"."min_val")) AND ("dhv"."volume" > "od"."volume") AND ("now"() < ("od"."news_time" + '00:05:00'::interval)));


ALTER VIEW "public"."signal" OWNER TO "postgres";

--
-- TOC entry 266 (class 1259 OID 16706)
-- Name: signal_arch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."signal_arch" (
    "id" integer NOT NULL,
    "tstz" timestamp with time zone,
    "code" character varying(16),
    "date_discovery" timestamp with time zone,
    "channel_source" character varying(64),
    "news_time" timestamp with time zone,
    "min_val" double precision,
    "max_val" double precision,
    "mean_val" double precision,
    "volume" double precision,
    "board" character varying(32),
    "min" double precision,
    "max" double precision,
    "last_volume" double precision,
    "count" bigint
);


ALTER TABLE "public"."signal_arch" OWNER TO "postgres";

--
-- TOC entry 267 (class 1259 OID 16709)
-- Name: signal_arch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE "public"."signal_arch_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."signal_arch_id_seq" OWNER TO "postgres";

--
-- TOC entry 4408 (class 0 OID 0)
-- Dependencies: 267
-- Name: signal_arch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE "public"."signal_arch_id_seq" OWNED BY "public"."signal_arch"."id";


--
-- TOC entry 409 (class 1259 OID 152968)
-- Name: tgchannels_ids; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."tgchannels_ids" (
    "title" character varying(64),
    "chat_id" bigint NOT NULL,
    "last_msg_id" bigint,
    "dt" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."tgchannels_ids" OWNER TO "postgres";

--
-- TOC entry 412 (class 1259 OID 172674)
-- Name: tgchannels_refresh_stat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."tgchannels_refresh_stat" (
    "bucket" bigint NOT NULL,
    "num" bigint
);


ALTER TABLE "public"."tgchannels_refresh_stat" OWNER TO "postgres";

--
-- TOC entry 410 (class 1259 OID 161168)
-- Name: tgchannels_timeout; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."tgchannels_timeout" (
    "success_calls" bigint,
    "sleep_time" double precision,
    "timeout" double precision,
    "dt" timestamp with time zone DEFAULT "now"(),
    "session" character varying(63)
);


ALTER TABLE "public"."tgchannels_timeout" OWNER TO "postgres";

--
-- TOC entry 268 (class 1259 OID 16710)
-- Name: tinkoff_params; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "public"."tinkoff_params" (
    "index" bigint,
    "name" "text",
    "ticker" "text",
    "class_code" "text",
    "figi" "text",
    "type" "text",
    "min_price_increment" "text",
    "currency" "text",
    "exchange" "text"
);


ALTER TABLE "public"."tinkoff_params" OWNER TO "postgres";

--
-- TOC entry 402 (class 1259 OID 149745)
-- Name: trd_mypos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."trd_mypos" AS
 WITH "pos_summary" AS (
         SELECT "united_pos"."code",
            "united_pos"."pos",
            "united_pos"."pnl",
            "united_pos"."volume"
           FROM "public"."united_pos"
        UNION
         SELECT 'ZTOTAL'::character varying AS "varchar",
            0,
            "sum"("united_pos"."pnl") AS "sum",
            "sum"("united_pos"."volume") AS "sum"
           FROM "public"."united_pos"
        ), "intervals" AS (
         SELECT COALESCE("l_up"."sec", "l_down"."sec") AS "code",
            "l_down"."price" AS "down_price",
            COALESCE("l_up"."price", (999999)::double precision) AS "up_price"
           FROM ("public"."df_levels" "l_up"
             FULL JOIN "public"."df_levels" "l_down" ON ((("l_up"."index" = ("l_down"."index" + 1)) AND ("l_up"."sec" = "l_down"."sec"))))
        ), "orders" AS (
         SELECT "orders_my"."code",
            "count"(*) AS "ordnum",
            "sum"("orders_my"."state") AS "actnum"
           FROM "public"."orders_my"
          GROUP BY "orders_my"."code"
        ), "plita_bid" AS (
         SELECT "bids"."code",
            "bids"."price" AS "bid",
            "bids"."quantity" AS "bid_qty"
           FROM "public"."report_plita" "bids"
          WHERE ("bids"."ba" = 'bid'::"text")
        ), "plita_ask" AS (
         SELECT "asks"."code",
            "asks"."price" AS "ask",
            "asks"."quantity" AS "ask_qty"
           FROM "public"."report_plita" "asks"
          WHERE ("asks"."ba" = 'ask'::"text")
        )
 SELECT "pos"."code",
    "pos"."pos",
    "pos"."pnl",
    "df_monitor"."new_price" AS "mktprice",
    "pos"."volume",
    "round"(("intervals"."down_price")::numeric, 4) AS "lower",
    "round"(("intervals"."up_price")::numeric, 4) AS "upper",
    "round"(((("df_monitor"."new_price" - "intervals"."down_price"))::numeric / (("intervals"."up_price" - "intervals"."down_price"))::numeric), 2) AS "levels",
    "df_monitor"."new_state",
    COALESCE("orders"."ordnum", (0)::bigint) AS "ordnum",
    COALESCE("orders"."actnum", (0)::bigint) AS "actnum",
    "plita_bid"."bid",
    "plita_bid"."bid_qty",
    "plita_ask"."ask",
    "plita_ask"."ask_qty"
   FROM ((((("pos_summary" "pos"
     LEFT JOIN "public"."df_monitor" "df_monitor" ON (("df_monitor"."code" = ("pos"."code")::"text")))
     LEFT JOIN "intervals" ON (((("pos"."code")::"text" = "intervals"."code") AND ("df_monitor"."new_price" >= "intervals"."down_price") AND ("df_monitor"."new_price" < "intervals"."up_price"))))
     LEFT JOIN "orders" ON ((("pos"."code")::"text" = ("orders"."code")::"text")))
     LEFT JOIN "plita_bid" ON ((("pos"."code")::"text" = "plita_bid"."code")))
     LEFT JOIN "plita_ask" ON ((("pos"."code")::"text" = "plita_ask"."code")))
  ORDER BY "pos"."code";


ALTER VIEW "public"."trd_mypos" OWNER TO "postgres";

--
-- TOC entry 269 (class 1259 OID 16715)
-- Name: trd_pos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."trd_pos" AS
 SELECT 1 AS "state",
    1 AS "quantity",
    ('POS'::"text" || "mntr"."code") AS "comment",
        CASE
            WHEN ("lvls"."down" = '0'::"text") THEN ("lvls"."mid" - ((4)::double precision * "lvls"."std"))
            ELSE "lvls"."sl"
        END AS "stop_loss",
    "lvls"."end" AS "take_profit",
    "lvls"."max_start" AS "barrier",
    1 AS "max_amount",
    1 AS "pause",
    "mntr"."code",
    1 AS "direction",
    ("now"() + '00:01:00'::interval) AS "end_time",
    "now"() AS "start_time",
    "mntr"."new_state",
    "mntr"."new_price",
    "mntr"."new_start",
    "mntr"."new_end",
    "lvls"."std",
    "lvls"."price" AS "next_resistance",
    "lvls"."min_start" AS "prev_resistance_std",
    "lvls"."sl",
    "lvls"."mid" AS "prev_resistance",
    "lvls"."down" AS "preprev_resistance",
    "lvls"."prev_end" AS "prev_take_profit"
   FROM ("public"."df_monitor" "mntr"
     LEFT JOIN ( SELECT "df_levels"."index",
            "df_levels"."price",
            "df_levels"."volume",
            "df_levels"."std",
            "df_levels"."sec",
            "df_levels"."min_start",
            "df_levels"."max_start",
            "df_levels"."end",
            "df_levels"."sl",
            "df_levels"."mid",
            "df_levels"."down",
            "df_levels"."prev_end",
            "df_levels"."next_sl",
            "df_levels"."implied_prob",
            "df_levels"."timestamp"
           FROM "public"."df_levels"
          WHERE ("df_levels"."max_start" > "df_levels"."min_start")) "lvls" ON (("mntr"."code" = "lvls"."sec")))
  WHERE (("right"("mntr"."code", 1) ~ '[0-9]'::"text") AND ("mntr"."new_price" >= "mntr"."old_price") AND ("lvls"."min_start" <= "mntr"."new_price") AND ("mntr"."new_price" <= "lvls"."max_start") AND ("mntr"."new_state" = 'start'::"text"));


ALTER VIEW "public"."trd_pos" OWNER TO "postgres";

--
-- TOC entry 404 (class 1259 OID 149759)
-- Name: vpnl; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."vpnl" AS
 SELECT "d"."time",
    (
        CASE
            WHEN (("d"."bs")::"text" = 'BUY'::"text") THEN 1
            ELSE '-1'::integer
        END * "d"."amount") AS "amount",
    "d"."code",
    "d"."price" AS "in_price",
    "q"."price",
    "d"."volume",
    "d"."broker_fees",
    ((((
        CASE
            WHEN (("d"."bs")::"text" = 'BUY'::"text") THEN 1
            ELSE '-1'::integer
        END)::double precision * "d"."volume") * (("q"."price" / "d"."price") - (1)::double precision)) - "d"."broker_fees") AS "pnl",
    "q"."lot"
   FROM ("public"."deals" "d"
     JOIN ( SELECT "futquotes"."code",
            (("futquotes"."bid" + "futquotes"."ask") / (2)::double precision) AS "price",
            1 AS "lot"
           FROM "public"."futquotes"
          WHERE ("futquotes"."bid" > (0)::double precision)
        UNION ALL
         SELECT "secquotes"."code",
            (("secquotes"."bid" + "secquotes"."ask") / (2)::double precision) AS "price",
            "secquotes"."lot"
           FROM "public"."secquotes"
          WHERE ("secquotes"."bid" > (0)::double precision)) "q" ON ((("d"."code")::"text" = ("q"."code")::"text")));


ALTER VIEW "public"."vpnl" OWNER TO "postgres";

--
-- TOC entry 405 (class 1259 OID 149764)
-- Name: vpnlext; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW "public"."vpnlext" AS
 SELECT "amount",
    "code",
    "mprice",
    "pnl",
    ((("amount")::double precision * "mprice") * ("lot")::double precision) AS "volume",
        CASE
            WHEN ("amount" = (0)::numeric) THEN (0)::double precision
            ELSE ((("mprice" * ("lot")::double precision) - "pnl") / ("amount")::double precision)
        END AS "breakevenprice"
   FROM ( SELECT "sum"("vpnl"."amount") AS "amount",
            "vpnl"."code",
            "avg"("vpnl"."price") AS "mprice",
            "sum"("vpnl"."pnl") AS "pnl",
            "avg"("vpnl"."lot") AS "lot"
           FROM "public"."vpnl"
          GROUP BY "vpnl"."code") "l";


ALTER VIEW "public"."vpnlext" OWNER TO "postgres";

--
-- TOC entry 4073 (class 2604 OID 16730)
-- Name: orders_auto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_auto" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."orders_auto_id_seq"'::"regclass");


--
-- TOC entry 4079 (class 2604 OID 149654)
-- Name: orders_my id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_my" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."orders_my_id_seq"'::"regclass");


--
-- TOC entry 4075 (class 2604 OID 16734)
-- Name: signal_arch id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."signal_arch" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."signal_arch_id_seq"'::"regclass");


--
-- TOC entry 4125 (class 2606 OID 16747)
-- Name: df_all_candles_t_arch candles_t_arch_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."df_all_candles_t_arch"
    ADD CONSTRAINT "candles_t_arch_constr" UNIQUE ("security", "datetime");


--
-- TOC entry 4120 (class 2606 OID 16749)
-- Name: df_all_candles_t candles_t_constr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."df_all_candles_t"
    ADD CONSTRAINT "candles_t_constr" UNIQUE ("security", "datetime");


--
-- TOC entry 4106 (class 2606 OID 16751)
-- Name: deals_ba_hist deals_ba_hist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_ba_hist"
    ADD CONSTRAINT "deals_ba_hist_pkey" PRIMARY KEY ("code", "price", "last_upd");


--
-- TOC entry 4175 (class 2606 OID 149606)
-- Name: deals_ba deals_ba_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_ba"
    ADD CONSTRAINT "deals_ba_pkey" PRIMARY KEY ("code", "price");


--
-- TOC entry 4116 (class 2606 OID 16753)
-- Name: deals_imp_arch deals_imp_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_imp_arch"
    ADD CONSTRAINT "deals_imp_arch_pkey" PRIMARY KEY ("deal_id", "tradedate");


--
-- TOC entry 4109 (class 2606 OID 16755)
-- Name: deals_imp deals_imp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_imp"
    ADD CONSTRAINT "deals_imp_pkey" PRIMARY KEY ("deal_id", "tradedate");


--
-- TOC entry 4202 (class 2606 OID 4423642)
-- Name: deals_imp_t deals_imp_t_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_imp_t"
    ADD CONSTRAINT "deals_imp_t_pkey" PRIMARY KEY ("price", "code", "datetime");


--
-- TOC entry 4118 (class 2606 OID 16757)
-- Name: deals_myhist deals_myhist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals_myhist"
    ADD CONSTRAINT "deals_myhist_pkey" PRIMARY KEY ("deal_id", "tradedate");


--
-- TOC entry 4192 (class 2606 OID 149758)
-- Name: deals deals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."deals"
    ADD CONSTRAINT "deals_pkey" PRIMARY KEY ("deal_id", "tradedate");


--
-- TOC entry 4127 (class 2606 OID 16761)
-- Name: df_all_candles_t_arch df_all_candles_t_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."df_all_candles_t_arch"
    ADD CONSTRAINT "df_all_candles_t_arch_pkey" PRIMARY KEY ("security", "datetime", "open", "high", "low", "close", "volume");


--
-- TOC entry 4151 (class 2606 OID 25650)
-- Name: df_volumes df_volumes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."df_volumes"
    ADD CONSTRAINT "df_volumes_pkey" PRIMARY KEY ("security", "tm");


--
-- TOC entry 4139 (class 2606 OID 34161)
-- Name: event_news event_news_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."event_news"
    ADD CONSTRAINT "event_news_pkey" PRIMARY KEY ("code", "news_time", "channel_source");


--
-- TOC entry 4173 (class 2606 OID 149601)
-- Name: func_stats func_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."func_stats"
    ADD CONSTRAINT "func_stats_pkey" PRIMARY KEY ("name");


--
-- TOC entry 4155 (class 2606 OID 138282)
-- Name: futprefix futprefix_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."futprefix"
    ADD CONSTRAINT "futprefix_pkey" PRIMARY KEY ("futprefix");


--
-- TOC entry 4167 (class 2606 OID 149531)
-- Name: futquotes futquotes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."futquotes"
    ADD CONSTRAINT "futquotes_pkey" PRIMARY KEY ("fullid");


--
-- TOC entry 4171 (class 2606 OID 149593)
-- Name: futquotesdiff futquotesdiff_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."futquotesdiff"
    ADD CONSTRAINT "futquotesdiff_pkey" PRIMARY KEY ("code");


--
-- TOC entry 4159 (class 2606 OID 34684)
-- Name: order_dividend order_dividend_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."order_dividend"
    ADD CONSTRAINT "order_dividend_pkey" PRIMARY KEY ("ticker");


--
-- TOC entry 4143 (class 2606 OID 16763)
-- Name: orders_auto orders_auto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_auto"
    ADD CONSTRAINT "orders_auto_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4180 (class 2606 OID 149671)
-- Name: orders_event_activator_jumps orders_event_activator_jumps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_event_activator_jumps"
    ADD CONSTRAINT "orders_event_activator_jumps_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4182 (class 2606 OID 149681)
-- Name: orders_event_activator_news orders_event_activator_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_event_activator_news"
    ADD CONSTRAINT "orders_event_activator_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4157 (class 2606 OID 34116)
-- Name: orders_event_activator orders_event_activator_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_event_activator"
    ADD CONSTRAINT "orders_event_activator_pkey1" PRIMARY KEY ("id");


--
-- TOC entry 4184 (class 2606 OID 149690)
-- Name: orders_event_activator_price orders_event_activator_price_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_event_activator_price"
    ADD CONSTRAINT "orders_event_activator_price_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4177 (class 2606 OID 149656)
-- Name: orders_my orders_my_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."orders_my"
    ADD CONSTRAINT "orders_my_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4186 (class 2606 OID 149712)
-- Name: pos_collat pk_pos_collat; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."pos_collat"
    ADD CONSTRAINT "pk_pos_collat" UNIQUE ("view", "type", "account", "code");


--
-- TOC entry 4188 (class 2606 OID 149717)
-- Name: pos_eq pk_pos_eq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."pos_eq"
    ADD CONSTRAINT "pk_pos_eq" UNIQUE ("firm", "account", "client_id", "settlement", "code");


--
-- TOC entry 4190 (class 2606 OID 149722)
-- Name: pos_fut pk_pos_fut; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."pos_fut"
    ADD CONSTRAINT "pk_pos_fut" UNIQUE ("code", "firm", "account", "type");


--
-- TOC entry 4145 (class 2606 OID 16771)
-- Name: pos_volmult pos_volmult_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."pos_volmult"
    ADD CONSTRAINT "pos_volmult_pkey" PRIMARY KEY ("code");


--
-- TOC entry 4199 (class 2606 OID 1283080)
-- Name: report_plita_tbl report_plita_tbl_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."report_plita_tbl"
    ADD CONSTRAINT "report_plita_tbl_pkey" PRIMARY KEY ("security", "datetime");


--
-- TOC entry 4165 (class 2606 OID 149524)
-- Name: secquotes secquotes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."secquotes"
    ADD CONSTRAINT "secquotes_pkey" PRIMARY KEY ("fullid");


--
-- TOC entry 4169 (class 2606 OID 149586)
-- Name: secquotesdiff secquotesdiff_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."secquotesdiff"
    ADD CONSTRAINT "secquotesdiff_pkey" PRIMARY KEY ("code");


--
-- TOC entry 4147 (class 2606 OID 16773)
-- Name: signal_arch signal_arch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."signal_arch"
    ADD CONSTRAINT "signal_arch_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4195 (class 2606 OID 152972)
-- Name: tgchannels_ids tgchannels_ids_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."tgchannels_ids"
    ADD CONSTRAINT "tgchannels_ids_pkey" PRIMARY KEY ("chat_id");


--
-- TOC entry 4197 (class 2606 OID 172888)
-- Name: tgchannels_refresh_stat tgchannels_refresh_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "public"."tgchannels_refresh_stat"
    ADD CONSTRAINT "tgchannels_refresh_stat_pkey" PRIMARY KEY ("bucket");


--
-- TOC entry 4103 (class 1259 OID 16774)
-- Name: code_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "code_idx" ON "public"."deals_ba_hist" USING "btree" ("code");


--
-- TOC entry 4104 (class 1259 OID 16775)
-- Name: code_last_upd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "code_last_upd" ON "public"."deals_ba_hist" USING "btree" ("last_upd" DESC NULLS LAST, "code");


--
-- TOC entry 4112 (class 1259 OID 138306)
-- Name: deals_imp_arch_code_expr_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "deals_imp_arch_code_expr_idx" ON "public"."deals_imp_arch" USING "btree" ("code", (("tradedate" + "time")) DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4113 (class 1259 OID 138303)
-- Name: deals_imp_arch_code_expr_price_bs_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "deals_imp_arch_code_expr_price_bs_idx" ON "public"."deals_imp_arch" USING "btree" ("code", (("tradedate" + "time")) DESC, "price", "bs") WITH ("deduplicate_items"='true');


--
-- TOC entry 4114 (class 1259 OID 138305)
-- Name: deals_imp_arch_code_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "deals_imp_arch_code_idx" ON "public"."deals_imp_arch" USING "btree" ("code") WITH ("deduplicate_items"='true');


--
-- TOC entry 4107 (class 1259 OID 4464177)
-- Name: deals_imp_expr_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "deals_imp_expr_idx" ON "public"."deals_imp" USING "btree" ((("tradedate" + "time")) DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4200 (class 1259 OID 4458051)
-- Name: deals_imp_t_code_datetime_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "deals_imp_t_code_datetime_idx" ON "public"."deals_imp_t" USING "btree" ("code", "datetime" DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4121 (class 1259 OID 149775)
-- Name: df_all_candles_t_security_datetime_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "df_all_candles_t_security_datetime_idx" ON "public"."df_all_candles_t" USING "btree" ("security", "datetime" DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4152 (class 1259 OID 25651)
-- Name: df_volumes_security_tm_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "df_volumes_security_tm_idx" ON "public"."df_volumes" USING "btree" ("security", "tm" DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4122 (class 1259 OID 16776)
-- Name: idx_candles_datetime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_candles_datetime" ON "public"."df_all_candles_t" USING "btree" ("datetime" DESC);


--
-- TOC entry 4123 (class 1259 OID 16777)
-- Name: idx_candles_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_candles_security" ON "public"."df_all_candles_t" USING "btree" ("security");


--
-- TOC entry 4110 (class 1259 OID 4469866)
-- Name: idx_deals_imp_tradedate_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_deals_imp_tradedate_time" ON "public"."deals_imp" USING "btree" ((("tradedate" + "time")));


--
-- TOC entry 4111 (class 1259 OID 4466920)
-- Name: idx_deals_imp_tradedate_time_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_deals_imp_tradedate_time_code" ON "public"."deals_imp" USING "btree" ((("tradedate" + "time")), "code");


--
-- TOC entry 4160 (class 1259 OID 78545)
-- Name: idx_futquoteshist_arch_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_futquoteshist_arch_lastupd" ON "public"."futquotesdiffhist_arch" USING "btree" ("last_upd" DESC);


--
-- TOC entry 4134 (class 1259 OID 16778)
-- Name: idx_futquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_futquoteshist_lastupd" ON "public"."futquotesdiffhist" USING "btree" ("last_upd" DESC);


--
-- TOC entry 4135 (class 1259 OID 16779)
-- Name: idx_futquoteshit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_futquoteshit" ON "public"."futquotesdiffhist" USING "btree" ("code");


--
-- TOC entry 4161 (class 1259 OID 78546)
-- Name: idx_futquoteshit_arch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_futquoteshit_arch" ON "public"."futquotesdiffhist_arch" USING "btree" ("code");


--
-- TOC entry 4141 (class 1259 OID 16780)
-- Name: idx_ord_disc_code_nt; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_ord_disc_code_nt" ON "public"."order_discovery" USING "btree" ("code", "news_time" DESC);


--
-- TOC entry 4136 (class 1259 OID 16781)
-- Name: idx_secquoteshist; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_secquoteshist" ON "public"."secquotesdiffhist" USING "btree" ("code");


--
-- TOC entry 4162 (class 1259 OID 78550)
-- Name: idx_secquoteshist_arch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_secquoteshist_arch" ON "public"."secquotesdiffhist_arch" USING "btree" ("code");


--
-- TOC entry 4163 (class 1259 OID 78551)
-- Name: idx_secquoteshist_arch_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_secquoteshist_arch_lastupd" ON "public"."secquotesdiffhist_arch" USING "btree" ("last_upd" DESC);


--
-- TOC entry 4137 (class 1259 OID 16785)
-- Name: idx_secquoteshist_lastupd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_secquoteshist_lastupd" ON "public"."secquotesdiffhist" USING "btree" ("last_upd" DESC);


--
-- TOC entry 4128 (class 1259 OID 16786)
-- Name: idx_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "idx_security" ON "public"."df_all_candles_t_arch" USING "btree" ("security");


--
-- TOC entry 4100 (class 1259 OID 16787)
-- Name: ix_analytics_beta_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_analytics_beta_index" ON "public"."analytics_beta" USING "btree" ("index");


--
-- TOC entry 4101 (class 1259 OID 16788)
-- Name: ix_analytics_future_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_analytics_future_index" ON "public"."analytics_future" USING "btree" ("index");


--
-- TOC entry 4102 (class 1259 OID 16789)
-- Name: ix_analytics_past_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_analytics_past_index" ON "public"."analytics_past" USING "btree" ("index");


--
-- TOC entry 4129 (class 1259 OID 16790)
-- Name: ix_df_all_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_df_all_levels_index" ON "public"."df_all_levels" USING "btree" ("index");


--
-- TOC entry 4130 (class 1259 OID 16791)
-- Name: ix_df_all_volumes_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_df_all_volumes_index" ON "public"."df_all_volumes" USING "btree" ("index");


--
-- TOC entry 4131 (class 1259 OID 16792)
-- Name: ix_df_bollinger_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_df_bollinger_index" ON "public"."df_bollinger" USING "btree" ("index");


--
-- TOC entry 4132 (class 1259 OID 16793)
-- Name: ix_df_levels_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_df_levels_index" ON "public"."df_levels" USING "btree" ("index");


--
-- TOC entry 4133 (class 1259 OID 16794)
-- Name: ix_df_monitor_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_df_monitor_index" ON "public"."df_monitor" USING "btree" ("index");


--
-- TOC entry 4178 (class 1259 OID 149662)
-- Name: ix_diffhist_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_diffhist_index" ON "public"."diffhist_t1510" USING "btree" ("index");


--
-- TOC entry 4099 (class 1259 OID 16797)
-- Name: ix_diffhist_t5_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_diffhist_t5_index" ON "public"."diffhist_t5" USING "btree" ("index");


--
-- TOC entry 4140 (class 1259 OID 16798)
-- Name: ix_events_jumps_hist_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_events_jumps_hist_index" ON "public"."events_jumps_hist" USING "btree" ("index");


--
-- TOC entry 4095 (class 1259 OID 16799)
-- Name: ix_orders_in_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_orders_in_index" ON "public"."orders_in" USING "btree" ("index");


--
-- TOC entry 4097 (class 1259 OID 16800)
-- Name: ix_orders_in_tcs_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_orders_in_tcs_index" ON "public"."orders_in_tcs" USING "btree" ("index");


--
-- TOC entry 4096 (class 1259 OID 16801)
-- Name: ix_orders_out_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_orders_out_index" ON "public"."orders_out" USING "btree" ("index");


--
-- TOC entry 4098 (class 1259 OID 16802)
-- Name: ix_orders_out_tcs_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_orders_out_tcs_index" ON "public"."orders_out_tcs" USING "btree" ("index");


--
-- TOC entry 4153 (class 1259 OID 25670)
-- Name: ix_public.df_monitor_level_0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_public.df_monitor_level_0" ON "public"."public.df_monitor" USING "btree" ("level_0");


--
-- TOC entry 4149 (class 1259 OID 16803)
-- Name: ix_tinkoff_params_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "ix_tinkoff_params_index" ON "public"."tinkoff_params" USING "btree" ("index");


--
-- TOC entry 4193 (class 1259 OID 152820)
-- Name: report_deal_imp_arch_t_code_datetime_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "report_deal_imp_arch_t_code_datetime_idx" ON "public"."report_deal_imp_arch_t" USING "btree" ("code", "datetime" DESC) WITH ("deduplicate_items"='true');


--
-- TOC entry 4148 (class 1259 OID 16804)
-- Name: signal_arch_tstz; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "signal_arch_tstz" ON "public"."signal_arch" USING "btree" ("tstz" DESC);


--
-- TOC entry 4209 (class 2620 OID 149594)
-- Name: futquotesdiff futquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "futquotesdiffhist_upd" AFTER INSERT OR UPDATE ON "public"."futquotesdiff" FOR EACH ROW EXECUTE FUNCTION "public"."futquotesdiffhistupd"();


--
-- TOC entry 4205 (class 2620 OID 149532)
-- Name: futquotes futquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "futquoteshisttrigger" AFTER UPDATE ON "public"."futquotes" FOR EACH ROW EXECUTE FUNCTION "public"."futquoteshistupd"();


--
-- TOC entry 4210 (class 2620 OID 149595)
-- Name: futquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "last_upd_rule" BEFORE INSERT OR UPDATE ON "public"."futquotesdiff" FOR EACH ROW EXECUTE FUNCTION "public"."last_upd_upd"();


--
-- TOC entry 4207 (class 2620 OID 149587)
-- Name: secquotesdiff last_upd_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "last_upd_rule" BEFORE INSERT OR UPDATE ON "public"."secquotesdiff" FOR EACH ROW EXECUTE FUNCTION "public"."last_upd_upd"();


--
-- TOC entry 4208 (class 2620 OID 149588)
-- Name: secquotesdiff secquotesdiffhist_upd; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "secquotesdiffhist_upd" AFTER INSERT OR UPDATE ON "public"."secquotesdiff" FOR EACH ROW EXECUTE FUNCTION "public"."secquotesdiffhistupd"();


--
-- TOC entry 4203 (class 2620 OID 149525)
-- Name: secquotes secquoteshisttrigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "secquoteshisttrigger" AFTER UPDATE ON "public"."secquotes" FOR EACH ROW EXECUTE FUNCTION "public"."secquoteshistupd"();

ALTER TABLE "public"."secquotes" DISABLE TRIGGER "secquoteshisttrigger";


--
-- TOC entry 4211 (class 2620 OID 149607)
-- Name: deals_ba updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "updated_at_rule" BEFORE INSERT OR UPDATE ON "public"."deals_ba" FOR EACH ROW EXECUTE FUNCTION "public"."updated_at_upd"();


--
-- TOC entry 4206 (class 2620 OID 149533)
-- Name: futquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "updated_at_rule" BEFORE INSERT OR UPDATE ON "public"."futquotes" FOR EACH ROW EXECUTE FUNCTION "public"."updated_at_upd"();


--
-- TOC entry 4204 (class 2620 OID 149526)
-- Name: secquotes updated_at_rule; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER "updated_at_rule" BEFORE INSERT OR UPDATE ON "public"."secquotes" FOR EACH ROW EXECUTE FUNCTION "public"."updated_at_upd"();


-- Completed on 2024-08-26 19:33:21 MSK

--
-- PostgreSQL database dump complete
--

