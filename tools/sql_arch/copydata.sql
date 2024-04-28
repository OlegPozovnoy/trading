CREATE EXTENSION postgres_fdw;

CREATE SERVER moscow
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '10.18.0.1', dbname 'test');

CREATE USER MAPPING FOR current_user
        SERVER moscow
        OPTIONS (user 'postgres');

DROP SCHEMA IF EXISTS mos CASCADE;

CREATE SCHEMA mos;

IMPORT FOREIGN SCHEMA public
    FROM SERVER moscow
    INTO mos;


insert into public.deals_imp_arch select * from mos.deals_imp_arch where tradedate > (CURRENT_DATE-9)
on conflict (deal_id, tradedate) do nothing;

insert into public.deals_myhist select * from mos.deals_myhist where tradedate > (CURRENT_DATE-9)
on conflict (deal_id,tradedate) do nothing;

truncate public.tinkoff_params;
insert into public.tinkoff_params select * from mos.tinkoff_params;


select
  table_name,
  pg_size_pretty(pg_total_relation_size(quote_ident(table_name))),
  pg_total_relation_size(quote_ident(table_name))
from information_schema.tables
where table_schema = 'public'
order by 3 desc;


killall snap-store
sudo snap refresh