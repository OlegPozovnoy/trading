import datetime
import json
import os
import asyncio

from dotenv import load_dotenv
from pyrogram import Client

import manual_order
import sql.get_table
import telegram
from monitor import send_df

import tools.clean_processes
from refresh import compose_td_datetime
from nlp import client

load_dotenv(dotenv_path='./my.env')

key = os.environ['tg_key']
api_id = os.environ['tg_api_id']
api_hash = os.environ['tg_api_hash']
channel_id = os.environ['tg_channel_id']
channel_id_urgent = os.environ['tg_channel_id_urgent']

conf_path = './tg_orders.json'


async def import_orders():
    async with Client("my_ccount_tgchannels", api_id, api_hash) as app:
        conf = json.load(open(conf_path, 'r'))
        last_check_date = datetime.datetime.strptime(conf['date'], "%Y-%m-%d %H:%M:%S")
        conf['date'] = last_check_date

        print(f"\nimporting orders")
        hist = app.get_chat_history(chat_id=channel_id_urgent, limit=5)
        async for msg in hist:
            if msg.date > last_check_date:
                conf['date'] = max(conf['date'], msg.date)
                try:
                    text = msg.text or ''
                    commands = text.split()
                    if len(commands) > 0 and commands[0] == 'My:':
                        command_dict = json.loads(" ".join(commands[1:]))
                        print(command_dict['name'])
                        GET_ORDERS_QUERY = """SELECT id, state, quantity, remains, barrier, max_amount, pause, code, 
                        direction,  provider, order_type, barrier_bound FROM public.orders_my;"""
                        params = dict()

                        if command_dict['name'] == 'get':
                            pass
                        elif command_dict['name'] == 'add':
                            params['quantity'] = command_dict['quantity']
                            params['code'] = command_dict['code']

                            params['order_nums'] = command_dict.get('order_nums') or 1
                            params['state'] = 0
                            params['max_amount'] = command_dict.get('max_amount') or 1
                            params['pause'] = command_dict.get('pause') or 1
                            params['barrier_up'] = command_dict.get('barrier_up')
                            params['barrier_down'] = command_dict.get('barrier_down')

                            await telegram.send_message(f"insertorder:{command_dict} {params}", urgent=True)
                            manual_order.execute_manual_order(quantity=params['quantity'], code=params['code'],
                                                              barrier_up=params['barrier_up'] ,
                                                              barrier_down=params['barrier_down'],
                                                              order_nums=params['order_nums'], state=params['state'], max_amount=params['max_amount'],
                                                              pause=params['pause'])

                        elif command_dict['name'] == 'set':
                            await telegram.send_message(f"setstate:{command_dict}", urgent=True)
                            query = f"""UPDATE public.orders_my SET state={int(command_dict['state'])} where id = {int(command_dict['id'])};"""
                            sql.get_table.exec_query(query)
                        else:
                            return

                        df_orders = sql.get_table.query_to_df(GET_ORDERS_QUERY)
                        await telegram.send_message(df_orders.to_string(justify='left', index=False), urgent=True)
                except Exception as e:
                    await telegram.send_message(f"processing error: {msg.text or ''} {str(e)}", urgent=True)
        conf['date'] = conf['date'].strftime("%Y-%m-%d %H:%M:%S")
        json.dump(conf, open(conf_path, 'w'))

if __name__ == "__main__":
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("tgorders", os.getpid(), 9999):
        print("something is already running")
        exit(0)

    try:
        asyncio.run(import_orders())
    except Exception as e:
        print(e)
    print(datetime.datetime.now())
