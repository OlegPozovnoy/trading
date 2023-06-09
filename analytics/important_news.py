from pymongo import MongoClient

import sql.get_table
import datetime

client = MongoClient()

urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
print(urgent_list)

res = ""
for ticker in urgent_list:
    from_date = datetime.datetime.today() - datetime.timedelta(days=7)
    to_date = datetime.datetime.today()

    news_collection = client.trading['news']

    for post in news_collection.find({"tags": ticker, "date": {"$gte": from_date, "$lt": to_date}}).sort("date",-1):
        res+="\n======================================================"
        res += f"\n{ticker} {post['channel_title']} {post['date']}"
        res += f"\n{post['text']} {post['caption']}"
        res+="\n======================================================"

print(res)
