import logging
import os
import uuid
from dotenv import load_dotenv

from tinkoff.invest import (
    Client,
    OrderDirection,
    OrderType,
    PostOrderResponse,
)
import sql.get_table

load_dotenv(dotenv_path='./my.env')

TOKEN = os.environ["TOKEN_WRITE"]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

engine = sql.get_table.engine
client = Client(TOKEN)


def place_order_tcs(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.001):
    global engine
    global client

    figi = get_figi(secCode)
    print(f'{figi =}')

    with Client(TOKEN) as client:
        response = client.users.get_accounts()
        account, *_ = response.accounts
        account_id = account.id

        order_id = uuid.uuid4().hex

        direction = OrderDirection.ORDER_DIRECTION_BUY if quantity > 0 else OrderDirection.ORDER_DIRECTION_SELL
        quantity = abs(quantity)

        order_tcs = {'quantity': abs(quantity),
                     'direction': direction,
                     'account_id': account_id,
                     'order_type': OrderType.ORDER_TYPE_MARKET,
                     'order_id': order_id,
                     'instrument_id': figi
                     }

        post_order_response: PostOrderResponse = client.orders.post_order(**order_tcs
                                                                          )

        status = post_order_response.execution_report_status
        print(status, post_order_response)


def get_figi(ticker):
    query = f"select figi from public.tinkoff_params where ticker='{ticker}' limit 1"
    return sql.get_table.query_to_list(query)[0]['figi']


if __name__ == "__main__":
    print(f'{TOKEN = }')
    place_order_tcs('SBER', -1)
