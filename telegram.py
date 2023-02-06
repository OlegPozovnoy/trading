key = "1337743768:AAFPfYpYqkbRkii5wZbH5PKtKrACKyifJAY"

api_id = "1961024"
api_hash = "6d5112fa19798f8e832a13587bfc4fe3"

import asyncio
from pyrogram import Client


async def test():
    async with Client("my_ccount", api_id, api_hash) as app:
        await app.send_message(-667947767, str("test"))


async def main():
    async with Client("my_ccount", api_id, api_hash) as app:
        # contact = await app.get_chats()
        # print(contact)
        # hist =  app.get_chat_history("@AK47pfl", limit=10)
        hist = app.get_chat_history(-1001656693918, limit=10)
        # async for msg in hist:
        async for msg in hist:
            print(msg.date, msg.text, msg.caption)
            await app.send_message(-312814047, str(msg.date) + " " + str(msg.caption) + " " + str(msg.text))

        #await app.log_out()


async def send_message(msg):
    async with Client("my_ccount", api_id, api_hash) as app:
        await app.send_message(-667947767, str(msg))
        #await app.log_out()


async def send_photo(filepath):
    async with Client("my_ccount", api_id, api_hash) as app:
        await app.send_photo(-667947767, filepath)
        #await app.log_out()


# asyncio.run(main())
asyncio.run(test())