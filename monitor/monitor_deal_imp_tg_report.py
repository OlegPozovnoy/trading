import os
import re
import sys
import asyncio
import datetime
from pathlib import Path

# Важно для запуска правой кнопкой из PyCharm:
# файл лежит в monitor/, но импорты и my.env лежат в корне проекта.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

(PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)

from dotenv import load_dotenv, find_dotenv

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sql.get_table
import telegram_send


load_dotenv(find_dotenv("my.env", True), verbose=True)

IMAGES_PATH = Path(os.environ["root_path"]) / "monitor" / "deal_imp_images"
IMAGES_PATH.mkdir(parents=True, exist_ok=True)

DEAL_IMP_CODES = ["MXU6", "CRU6", "VBU6", "BRU6", "SSU6"]

def get_deal_imp_image_filename(code):
    return f"deal_imp_{safe_filename(code)}.png"

def sql_str(value):
    return "'" + str(value).replace("'", "''") + "'"


def safe_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))


def get_active_codes(hours=3, min_rows=10):
    query = f"""
        SELECT code
        FROM public.deals_imp
        WHERE tradedate + "time" >= NOW() - interval '{int(hours)} hours'
          AND code IS NOT NULL
          AND price IS NOT NULL
        GROUP BY code
        HAVING COUNT(*) >= {int(min_rows)}
        ORDER BY code
    """
    df = sql.get_table.query_to_df(query)
    return df["code"].tolist()


def load_time_series(code, hours=3, row_limit=50000):
    query = f"""
        SELECT *
        FROM (
            SELECT
                date_trunc('second', tradedate + "time") AS datetime,

                AVG(price) AS price,

                SUM(COALESCE(amount, 0)) AS total_amount,

                SUM(
                    CASE
                        WHEN upper(COALESCE(bs, '')) IN ('B', 'BUY') THEN COALESCE(amount, 0)
                        WHEN upper(COALESCE(bs, '')) IN ('S', 'SELL') THEN -COALESCE(amount, 0)
                        ELSE 0
                    END
                ) AS net_amount,

                SUM(COALESCE(volume, 0)) AS total_volume,

                SUM(
                    CASE
                        WHEN upper(COALESCE(bs, '')) IN ('B', 'BUY') THEN COALESCE(volume, 0)
                        WHEN upper(COALESCE(bs, '')) IN ('S', 'SELL') THEN -COALESCE(volume, 0)
                        ELSE 0
                    END
                ) AS net_volume,

                AVG(open_interest) AS avg_open_interest,

                COUNT(*) AS deals_count
            FROM public.deals_imp
            WHERE code = {sql_str(code)}
              AND tradedate + "time" >= NOW() - interval '{int(hours)} hours'
              AND price IS NOT NULL
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT {int(row_limit)}
        ) t
        ORDER BY datetime
    """
    return sql.get_table.query_to_df(query)


def load_horizontal_volumes(code, hours=3):
    """
    Аналог Superset horizontal_volumes:
    X-axis = price
    metrics = SUM(total_amount), SUM(net_amount)
    """
    query = f"""
        SELECT
            price::float8 AS price,

            SUM(COALESCE(amount, 0)) AS total_amount,

            SUM(
                CASE
                    WHEN upper(COALESCE(bs, '')) IN ('B', 'BUY') THEN COALESCE(amount, 0)
                    WHEN upper(COALESCE(bs, '')) IN ('S', 'SELL') THEN -COALESCE(amount, 0)
                    ELSE 0
                END
            ) AS net_amount,

            SUM(COALESCE(volume, 0)) AS total_volume,

            SUM(
                CASE
                    WHEN upper(COALESCE(bs, '')) IN ('B', 'BUY') THEN COALESCE(volume, 0)
                    WHEN upper(COALESCE(bs, '')) IN ('S', 'SELL') THEN -COALESCE(volume, 0)
                    ELSE 0
                END
            ) AS net_volume,

            COUNT(*) AS deals_count
        FROM public.deals_imp
        WHERE code = {sql_str(code)}
          AND tradedate + "time" >= NOW() - interval '{int(hours)} hours'
          AND price IS NOT NULL
        GROUP BY price
        ORDER BY price
    """
    return sql.get_table.query_to_df(query)


def plot_deal_imp_dashboard(code, df_ts, df_hv, hours=3):
    IMBALANCE_WINDOW = "3min"

    df_ts = df_ts.copy()
    df_ts["datetime"] = pd.to_datetime(df_ts["datetime"])
    df_ts = df_ts.sort_values("datetime")

    df_ts["cum_net_amount"] = df_ts["net_amount"].fillna(0).cumsum()

    df_roll = df_ts.set_index("datetime")
    roll_net = df_roll["net_amount"].fillna(0).rolling(IMBALANCE_WINDOW).sum()
    roll_total = df_roll["total_amount"].fillna(0).rolling(IMBALANCE_WINDOW).sum()
    df_ts["imbalance"] = (roll_net / roll_total.where(roll_total != 0)).values

    if len(df_hv) > 0:
        df_hv = df_hv.copy().sort_values("price")

    filepath = IMAGES_PATH / get_deal_imp_image_filename(code)

    fig, axes = plt.subplots(2, 2, figsize=(18, 11))
    fig.suptitle(
        f"{code} | public.deals_imp | last {hours}h | {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        fontsize=13,
    )

    ax_pi = axes[0, 0]
    ax_hv = axes[0, 1]
    ax_pn = axes[1, 0]
    ax_imb = axes[1, 1]

    c_price = "#d62728"      # price всегда красный
    c_oi = "#17becf"         # open interest
    c_total = "#1f77b4"      # total amount
    c_net = "#2ca02c"        # net amount / imbalance
    c_cum = "#9467bd"        # cumulative net amount

    # 1. price_interest
    ax_pi_r = ax_pi.twinx()

    l_oi, = ax_pi.plot(
        df_ts["datetime"],
        df_ts["avg_open_interest"],
        color=c_oi,
        label=f"AVG(open_interest), {code}",
    )
    l_price, = ax_pi_r.plot(
        df_ts["datetime"],
        df_ts["price"],
        color=c_price,
        label=f"AVG(price), {code}",
    )

    ax_pi.set_title("price_interest")
    ax_pi.set_ylabel("AVG(open_interest)")
    ax_pi_r.set_ylabel("AVG(price)")
    ax_pi.grid(True, alpha=0.3)
    ax_pi.legend([l_price, l_oi], [l_price.get_label(), l_oi.get_label()], loc="upper right")

    # 2. horizontal_volumes
    if len(df_hv) > 0:
        ax_hv.plot(df_hv["price"], df_hv["total_amount"], color=c_total, label="SUM(total_amount)")
        ax_hv.plot(df_hv["price"], df_hv["net_amount"], color=c_net, label="SUM(net_amount)")
        ax_hv.legend(loc="upper right")
    else:
        ax_hv.text(0.5, 0.5, "No price data", ha="center", va="center", transform=ax_hv.transAxes)

    ax_hv.set_title("horizontal_volumes")
    ax_hv.set_xlabel("price")
    ax_hv.grid(True, alpha=0.3)

    # 3. price_netamount: cumulative net amount
    ax_pn_r = ax_pn.twinx()

    l_cum, = ax_pn.plot(
        df_ts["datetime"],
        df_ts["cum_net_amount"],
        color=c_cum,
        label="CUM(SUM(net_amount))",
    )
    l_price2, = ax_pn_r.plot(
        df_ts["datetime"],
        df_ts["price"],
        color=c_price,
        label="AVG(price)",
    )

    ax_pn.axhline(0, color="black", linewidth=0.8, alpha=0.35)
    ax_pn.set_title("price_netamount")
    ax_pn.set_ylabel("CUM(SUM(net_amount))")
    ax_pn_r.set_ylabel("AVG(price)")
    ax_pn.grid(True, alpha=0.3)
    ax_pn.legend([l_price2, l_cum], [l_price2.get_label(), l_cum.get_label()], loc="upper right")

    # 4. imbalance
    ax_imb_r = ax_imb.twinx()

    l_imb, = ax_imb.plot(
        df_ts["datetime"],
        df_ts["imbalance"],
        color=c_net,
        label=f"Imbalance {IMBALANCE_WINDOW}",
    )
    l_price3, = ax_imb_r.plot(
        df_ts["datetime"],
        df_ts["price"],
        color=c_price,
        label="AVG(price)",
        alpha=0.85,
    )

    ax_imb.axhline(0, color="black", linewidth=0.8, alpha=0.35)
    ax_imb.set_ylim(-1.05, 1.05)
    ax_imb.set_title(f"imbalance_{IMBALANCE_WINDOW}")
    ax_imb.set_ylabel(f"SUM(net_amount) / SUM(total_amount), {IMBALANCE_WINDOW}")
    ax_imb_r.set_ylabel("AVG(price)")
    ax_imb.grid(True, alpha=0.3)
    ax_imb.legend([l_price3, l_imb], [l_price3.get_label(), l_imb.get_label()], loc="upper right")

    for ax in [ax_pi, ax_pn, ax_imb]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(filepath, dpi=110)
    plt.close(fig)

    return str(filepath)


def prepare_deal_imp_images(codes, hours=3, row_limit=50000):
    codes = pd.Series(codes).dropna().astype(str).drop_duplicates()

    for code in codes:
        df_ts = load_time_series(code, hours=hours, row_limit=row_limit)

        if len(df_ts) == 0:
            continue

        df_hv = load_horizontal_volumes(code, hours=hours)

        plot_deal_imp_dashboard(
            code=code,
            df_ts=df_ts,
            df_hv=df_hv,
            hours=hours,
        )


def send_all_deal_imp_graph(
    urgent_list=None,
    hours=3,
    row_limit=50000,
):
    from monitor import send_all_graph

    if urgent_list is None:
        urgent_list = []

    send_all_graph(
        codes=DEAL_IMP_CODES,
        urgent_list=urgent_list,
        image_dir=IMAGES_PATH,
        prepare_func=lambda codes: prepare_deal_imp_images(
            codes=codes,
            hours=hours,
            row_limit=row_limit,
        ),
        filename_func=get_deal_imp_image_filename,
        send_nonurgent=True,
    )


async def build_and_queue_deal_imp_reports(
    codes=None,
    hours=3,
    urgent=False,
    min_rows=10,
    row_limit=50000,
    max_codes=None,
):
    """
    codes=None
        Построить графики по всем инструментам из public.deals_imp за последние hours.

    codes=["MXU6", "SMLT"]
        Построить только по заданному списку.

    urgent=True
        Кладёт картинки в tg_buffer/urgent.

    urgent=False
        Кладёт картинки в tg_buffer/normal.
    """

    if codes is None:
        codes = get_active_codes(hours=hours, min_rows=min_rows)

    codes = list(codes)

    if max_codes is not None:
        codes = codes[:int(max_codes)]

    sent = 0
    skipped = 0
    failed = 0

    for code in codes:
        try:
            df_ts = load_time_series(code, hours=hours, row_limit=row_limit)

            if len(df_ts) == 0:
                skipped += 1
                continue

            df_hv = load_horizontal_volumes(code, hours=hours)

            filepath = plot_deal_imp_dashboard(code, df_ts, df_hv, hours=hours)

            await telegram_send.send_photo(filepath, urgent=urgent)
            sent += 1

        except Exception as e:
            failed += 1
            await telegram_send.send_message(
                f"deal_imp report failed for {code}: {e}",
                urgent=True,
            )

    await telegram_send.send_message(
        f"deal_imp reports queued: sent={sent}, skipped={skipped}, failed={failed}, hours={hours}",
        urgent=urgent,
    )




if __name__ == "__main__":
    asyncio.run(
        build_and_queue_deal_imp_reports(
            codes=["MXU6","CRU6", "VBU6", "AKU6", 'BRQ6'],   # None = по всем инструментам
            hours=9,
            urgent=False,
            min_rows=10,
            row_limit=50000,
            max_codes=None,
        )
    )