from pymongo import MongoClient

import sql.get_table
import datetime

client = MongoClient()


def important_news():
    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    print(urgent_list)

    res = ""
    for ticker in urgent_list:
        from_date = datetime.datetime.today() - datetime.timedelta(days=7)
        to_date = datetime.datetime.today()

        news_collection = client.trading['news']
        res = ""
        for post in news_collection\
                .find({"tags": ticker, "date": {"$gte": from_date, "$lt": to_date}})\
                .sort("date", -1):

            res += "\n======================================================"
            res += f"\n{ticker} {post['channel_title']} {post['date']}"
            res += f"\n{post['text']} {post['caption']}"
            res += "\n======================================================"
    return res


def all_news():
    from_date = datetime.datetime.today() - datetime.timedelta(days=7)
    to_date = datetime.datetime.today() + datetime.timedelta(days=1)

    news_collection = client.trading['news']
    res = ""
    for post in news_collection\
            .find({"date": {"$gte": from_date, "$lt": to_date}})\
            .sort([("channel_title", 1), ("date", 1)]):

        res += "\n\nСледующая новость."
        res += f"\nКанал {post['channel_title']} {str(post['date'])[0:-3]}."
        res += f"\n{post['text']} {post['caption']}"
    return res


with open("recent_news.txt", "w") as f:
    f.write(all_news())
