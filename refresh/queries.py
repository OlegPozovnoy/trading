def get_query_fut_upd(current_time):
    """
    перенос полей из fut_quotes в futquotesdiff
    есть openinterest
    volume_wa - для расчета скачков на уровне тика, если текущий больше среднего - считаем аномалией
    min_5mins, max_5mins - раз в 5 минут сбрасываем таймер, считаем скачком если выпрыгнули из интервала min_5mins, max_5mins
    :return: строку с запросом
    """
    return f"""
    MERGE INTO public.futquotesdiff fqd
    USING public.futquotes fq
    ON fq.code = fqd.code
    WHEN MATCHED THEN
    UPDATE SET 
        bid = fq.bid, 
        ask = fq.ask, 
        volume = fq.volume, 
        openinterest = fq.openinterest, 
        bidamount = fq.bidamount, 
        askamount = fq.askamount, 
        bid_inc = fq.bid - fqd.bid, 
        ask_inc = fq.ask - fqd.ask, 
        volume_inc = fq.volume - fqd.volume, 
        updated_at = fq.updated_at, 
        last_upd = '{current_time}',
        volume_wa = coalesce(volume_wa,0)* 119/120 + (fq.volume - fqd.volume) / 120,   
        min_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM TIMESTAMP '{current_time}') 
                            and extract (minute from TIMESTAMP '{current_time}')%5=0 
                            then fq.ask else LEAST(fqd.min_5mins, fq.ask) end,
        max_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM TIMESTAMP '{current_time}') 
                            and extract (minute from TIMESTAMP '{current_time}')%5=0 
                            then fq.bid else GREATEST(fqd.max_5mins, fq.bid) end
    WHEN NOT MATCHED THEN
    INSERT (code, bid, bidamount, ask, askamount, volume, openinterest, bid_inc, ask_inc, volume_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins) 
    VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, fq.openinterest, 0, 0, 0, fq.updated_at, '{current_time}', 0, fq.ask, fq.bid);
    """


def get_query_sec_upd(current_time):
    """
    перенос полей из sec_quotes в secquotesdiff
    volume_wa - для расчета скачков на уровне тика, если текущий больше среднего - считаем аномалией
    min_5mins, max_5mins - раз в 5 минут сбрасываем таймер, считаем скачком если выпрыгнули из интервала min_5mins, max_5mins
    :return: строку с запросом
    """

    return f"""
    MERGE INTO public.secquotesdiff fqd
    USING public.secquotes fq
    ON fq.code = fqd.code
    WHEN MATCHED THEN
    UPDATE SET 
    bid = fq.bid, 
    ask = fq.ask, 
    volume = fq.volume, 
    bidamount=fq.bidamount, 
    askamount=fq.askamount, 
    bid_inc = fq.bid - fqd.bid, 
    ask_inc = fq.ask-fqd.ask, 
    volume_inc = fq.volume-fqd.volume, 
    updated_at=fq.updated_at, 
    last_upd = '{current_time}',
    volume_wa = coalesce(volume_wa,0)* 119/120 + (fq.volume - fqd.volume) / 120,   
    min_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM TIMESTAMP '{current_time}') 
                            and extract (minute from TIMESTAMP '{current_time}')%5=0 
                            then fq.ask else LEAST(fqd.min_5mins, fq.ask) end,
    max_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM TIMESTAMP '{current_time}') 
                            and extract (minute from TIMESTAMP '{current_time}')%5=0 
                            then fq.bid else GREATEST(fqd.max_5mins, fq.bid) end
    WHEN NOT MATCHED THEN
    INSERT (code, bid, bidamount, ask, askamount, volume, bid_inc, ask_inc, volume_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins) 
    VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, 0, 0, 0, fq.updated_at, '{current_time}', 0, fq.ask, fq.bid);
    """


def get_query_signals_upd():
    """
    переносим все из public.signal в public.signal_arch
    сигнал основан на order_discovery и diffhistview (который кажется был долгим, минмакс за последнюю минуту из futdiffhist)
    условия:
    1) (dhv.max - dhv.min) > (od.max_val - od.min_val)
    2) dhv.volume > od.volume
    3) now() < (od.news_time + '00:05:00'::interval)
    :return: запрос
    """
    return """
    insert into public.signal_arch(tstz, code, date_discovery, channel_source, news_time, min_val, max_val, mean_val, volume, board, min, max, last_volume, count)
    select * from public.signal;
    """


def get_query_bidask_upd():
    """
    как в futquoteshist: копируем deals_ba_view в deals_ba_hist
    обновляем deals_ba_t1 из deals_ba (перестраивая deals_ba_view)
    """
    return """
    BEGIN;
    INSERT INTO deals_ba_hist SELECT * FROM deals_ba_view;
    TRUNCATE TABLE deals_ba_t1;
    INSERT INTO deals_ba_t1 SELECT * FROM deals_ba;
    COMMIT;
    """


def get_query_sl_tp():
    """
    запрос возвращает список ордеров с stop_loss/take_profit в поле tpsl и все параметры из allquotes
    :return: запрос
    """
    return """
    SELECT 
        CASE 
            WHEN (direction = 1 AND bid > take_profit) OR (direction = -1 AND ask < take_profit) THEN 1
            ELSE -1 
        END AS tpsl,
        *
    FROM allquotes
    WHERE 
        end_time IS NULL AND
        (
            (direction = 1 AND bid > take_profit) OR
            (direction = -1 AND ask < take_profit) OR
            (direction = -1 AND bid > stop_loss) OR
            (direction = 1 AND ask < stop_loss)
        )
    """


def get_query_deact_by_endtime():
    """
    ставим state = 0 ордерам с уже прошедшим end_time
    :return: запрос
    """
    return "update public.orders_my set state=0 where now() > end_time"


def get_query_store_jump_events():
    """
    переносим public.jump_events в public.events_jumps_hist
    diffhist_t1510 - мин макс середняя цена за 15-10 минут до сейчас
    условия на jump:
    1) обьем больше чем минутный: (dh.volume::double precision * dh.max / 10::double precision) < fq.volume_inc
    2) вышли за минмакс: AND (fq.ask < dh.min OR fq.bid > dh.max)
    :return:
    """
    return """insert into public.events_jumps_hist 
    (code, min, max, mean, volume, count, bid, bidamount, ask, askamount, volume_inc, bid_inc, ask_inc, 
    updated_at, last_upd, volume_wa, process_time, jump_prct, out_prct, volume_peak, out_std)
    select * from public.jump_events;"""


def get_query_events_update_news():
    """
    обновляем таблицу orders_event_activator_news из сорса event_news куда заливаются все новости
    фильтры: тикер, кейворд, канал
    """
    return """
            update orders_event_activator_news oea
            set is_activated = true,
            activate_time = now()
            from event_news en
            where is_activated = false 
            and oea.ticker = en.code 
            and oea.keyword = en.keyword
            and news_time between start_date and end_date
            and (length(oea.channel_source) = 0 or oea.channel_source = en.channel_source)
            """


def get_query_events_update_jumps():
    """
    обновляем таблицу orders_event_activator_jumps из сорса events_jumps_hist
    фильтры: тикер, jump_prct, out_prct, volume_peak, out_std
    """
    return """
            update orders_event_activator_jumps oeaj
            set is_activated = true,
            activate_time = now()
            from jump_events ejh
            where is_activated = false 
            and oeaj.ticker = ejh.code 
            and ejh.process_time between oeaj.start_date and oeaj.end_date
            and abs(ejh.jump_prct) > coalesce(oeaj.jump_prct,0)
            and abs(ejh.out_prct) > coalesce(oeaj.out_prct,0)
            and ejh.volume_peak > coalesce(oeaj.volume_peak,0)
            and abs(ejh.out_std) > coalesce(oeaj.out_std,0)
    """


def get_query_events_update_prices():
     return      """    
     UPDATE orders_event_activator_price oeap
    SET is_activated = true,
        activate_time = now()
    FROM allquotes_mini aqm
    WHERE oeap.is_activated = false 
        AND oeap.ticker = aqm.code 
        AND NOW() BETWEEN oeap.start_date AND oeap.end_date
        AND (
            (oeap.price_limit < 0 AND aqm.ask < -oeap.price_limit) OR
            (oeap.price_limit > 0 AND aqm.bid > oeap.price_limit)
        )
     """


def get_remove_sec_duplicates():
    """
    убираем дубликаты в таблице sec_quotes, оставляя одну строку
    :return:
    """
    return """
    WITH ranked_quotes AS (
        SELECT 
            code, 
            updated_at, 
            ctid,
            row_number() OVER (
                PARTITION BY code 
                ORDER BY updated_at DESC
            ) AS row_num
        FROM secquotes
    )
    DELETE FROM secquotes
    WHERE ctid IN (
        SELECT 
            ctid
        FROM ranked_quotes
        WHERE row_num > 1
    );
    """

def get_remove_fut_duplicates():
    """
    убираем дубликаты в таблице sec_quotes, оставляя одну строку
    :return:
    """
    return """
    WITH ranked_quotes AS (
        SELECT 
            code, 
            updated_at, 
            ctid,
            row_number() OVER (
                PARTITION BY code 
                ORDER BY updated_at DESC
            ) AS row_num
        FROM futquotes
    )
    DELETE FROM futquotes
    WHERE ctid IN (
        SELECT 
            ctid
        FROM ranked_quotes
        WHERE row_num > 1
    );
    """
