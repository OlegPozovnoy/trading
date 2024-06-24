import sql.get_table


def update_deals_imp_t():
    query = """
    INSERT INTO deals_imp_t
    SELECT *
    FROM report_deal_imp
    WHERE
        (SELECT COUNT(*) FROM deals_imp_t) = 0
        OR
        datetime > (
            SELECT MIN(max_datetime) FROM (
                SELECT
                    code,
                    MAX(datetime) AS max_datetime
                FROM
                    deals_imp_t
                GROUP BY
                    code
            ) AS subquery
        )
    ON CONFLICT (price, code, datetime) DO NOTHING;
        
    WITH latest_row AS (
        SELECT
            code,
            MAX(datetime) AS max_datetime
        FROM
            deals_imp_t
        GROUP BY
            code
    )
    DELETE FROM deals_imp_t
    USING latest_row
    WHERE deals_imp_t.code = latest_row.code
    AND deals_imp_t.datetime = latest_row.max_datetime;
    """
    sql.get_table.exec_query(query)
