import asyncio
import asyncpg

async def query_product(pool,query):
    async with pool.acquire() as connection:
        return await connection.execute(query)

async def exec_list(query_list):
    async with asyncpg.create_pool(host='127.0.0.1',
    port=5432,
    user='postgres',
    database='test',
    min_size=4,
    max_size=4) as pool:
        await asyncio.gather(*[query_product(pool, query) for query in query_list])

