import datetime
import subprocess

import sql.get_table
from nlp import client



def important_news(days=1):
    urgent_list = [x[0] for x in sql.get_table.exec_query("SELECT code	FROM public.united_pos;")]
    print(urgent_list)

    urgent_list = ['SBER', 'SMLT', 'ALRS', 'MAGN', 'MGNT', 'LKOH', 'NLMK', 'CHMF']
    urgent_list = ['FIVE','MGNT','VTBR','SBRF','TCSI','ROSN','LKOH','SIBN','SNGR','TRNF','TATN','GAZR','NOTK','SMLT'
        ,'NLMK','MAGN','CHMF','GMKN','RUAL','ALRS','PLZL','MOEX','OZON','FLOT','FEES','IRAO','MTSI','YNDF','MAIL',
                   'RTSM', 'SNGP', 'POLY', 'HYDR', 'AFLT', 'PHOR', 'MTLR', 'PIKK', 'AFKS', 'POSI']

    urgent_list = ['FIVE','MGNT','VTBR','SBRF','TCSI','ROSN','LKOH','SIBN','TRNF','TATN','GAZR','NOTK','SMLT'
        ,'NLMK','MAGN','CHMF','GMKN','ALRS','PLZL','OZON','FLOT','IRAO','MTSI','YNDF',
                   'RTSM', 'POLY', 'HYDR', 'PHOR', 'MTLR']
    #urgent_list = ['FIVE','MGNT','SBRF','VTBR','ROSN','LKOH','SIBN','TRNF','TATN','NOTK','SMLT'
    #    ,'NLMK','MAGN','CHMF','RUAL','ALRS', 'OZON','FLOT','FEES','IRAO','MTSI','YNDF','MAIL']
    # urgent_list = ['FIVE','MGNT','VTBR','SBRF','TCSI','ROSN','LKOH','SIBN','SNGR','TRNF','TATN','NOTK','SMLT'
    #     ,'NLMK','MAGN','CHMF','OZON','FLOT','FEES']
    # "SRZ3"     "LKZ3"     "NMZ3"     "RNZ3"     "MGZ3"     "MNZ3"     "FVZ3"     "YNZ3"
    # urgent_list = ['SBRF','LKOH','NLMK','ROSN','TCSI','MAGN','MGNT','FIVE','YNDF','TRNF','VTBR']
    # urgent_list = ['SBRF', 'LKOH', 'NLMK', 'ROSN', 'TCSI', 'MAGN', 'MGNT', 'FIVE', 'YNDF', 'TRNF', 'VTBR']
    # urgent_list = ['MGNT']

    res = ""
    for ticker in urgent_list:
        print(ticker)
        from_date = datetime.datetime.today() - datetime.timedelta(days=days)
        to_date = datetime.datetime.today()

        news_collection = client.trading['news']
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


with open("important.txt", "w") as f:
    f.write(important_news())

subprocess.run(["python", "send_email.py"])
# with open("recent_news.txt", "w") as f:
#     f.write(all_news())
