from Transactions import place_order_tcs


def send_hft(tags, quantity):
    for secCode in tags:
        place_order_tcs(secCode, quantity=quantity, price_bound=None, max_quantity=quantity, comment="hafata",
                        maxspread=0.002, money_limit=300000)
