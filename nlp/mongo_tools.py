import datetime
import logging
from collections import defaultdict
from typing import List

from bson.objectid import ObjectId
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

import sql
from sql import get_table
from tools.utils import sync_timed
from nlp import client

logger = logging.getLogger()


def activate_all_channels(is_active, username=None):
    names_collection = client.trading['tg_channels']

    filter_str = {} if username is None else {'username': username}

    for document in names_collection.find(filter_str):
        res = names_collection.update_one(document, {'$set': {'is_active': is_active}})
        print(res)


def deactivate_channel(username, is_active=0):
    names_collection = client.trading['tg_channels']

    for document in names_collection.find({'username': username}):
        res = names_collection.update_one(document, {'$set': {'is_active': is_active}})
        print(res)


def remove_field(db, field_name):
    names_collection = client.trading[db]
    names_collection.update_many({}, {'$unset': {f'{field_name}': ''}}, False)


def remove_channel(channel_name):
    news_collection = client.trading['news']
    channels_collection = client.trading['tg_channels']

    news_filter = {'channel_username': channel_name}
    tg_filter = {'username': channel_name}

    for item in news_collection.find(news_filter):
        print(item)
        news_collection.delete_one(item)

    for item in channels_collection.find(tg_filter):
        print(item)
        channels_collection.delete_one(item)


@sync_timed()
def get_active_channels(private=True):
    names_collection = client.trading['tg_channels']
    result = []
    for document in names_collection.find({'is_active': 1}):
        if private and 'private' in document['tags']:
            result.append(document)
        elif private == False and 'private' not in document['tags']:
            result.append(document)
    return result


def get_news_from_channels(username):
    names_collection = client.trading['news']
    result = []  #channel_title 'channel_username':

    for document in names_collection.find({'channel_username': username}):
        result.append(document)
    return result


@sync_timed()
def update_tg_msg_count(username, count):
    names_collection = client.trading['tg_channels']
    names_collection.update_one({'username': username}, {'$set': {'count': count}})
    logger.info(names_collection.find_one({'username': username}))


def remove_tag_word(ticker, tag):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    print(set(instrument['namee']), {tag})
    new_tags = list(set(instrument['namee']) - {tag})
    print(instrument, "->", new_tags)
    instrument_collection.update_one({'ticker': ticker}, {'$set': {'namee': new_tags}})


def add_tag_word(ticker, tag):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    new_tags = set(instrument['namee'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'ticker': ticker}, {'$set': {'namee': list(new_tags)}})


def get_ticker_tags():
    instrument_collection = client.trading['trading']
    instruments = instrument_collection.find({})
    res = []
    for instrument in instruments:
        for tag in instrument['namee']:
            res.append((instrument['ticker'], tag))
    return pd.DataFrame(res, columns=['ticker', 'tag'])


def get_instrument(ticker):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    print(instrument)


def add_tag_channel(query, tag):
    instrument_collection = client.trading['tg_channels']
    instrument = instrument_collection.find_one(query)
    if 'tags' not in instrument: instrument['tags'] = []
    new_tags = set(instrument['tags'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'_id': instrument['_id']}, {'$set': {'tags': list(new_tags)}})


def remove_tag_channel(query, tag):
    instrument_collection = client.trading['tg_channels']
    instrument = instrument_collection.find_one(query)
    new_tags = set(instrument['tags'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'_id': instrument['_id']}, {'$set': {'tags': list(new_tags)}})


@sync_timed()
def renumerate_channels(is_active=False):
    out_id = 0
    instrument_collection = client.trading['tg_channels']

    query = {"is_active": 1} if is_active else {}

    for item in instrument_collection.find(query):
        out_id += 1
        instrument_collection.update_one(item, {'$set': {'out_id': out_id}})


@sync_timed()
def remove_news_duplicates():
    news_collection = client.trading['news']

    df_list = []
    for item in tqdm(news_collection.find()):
        df_list.append([item['_id'], item['date'], item['channel_username']])

    res = pd.DataFrame(df_list, columns=['id', 'date', 'username'])
    res.sort_values(['date', 'username'], inplace=True)
    res = res.reset_index(drop=True)

    cnt, deleted = 0, 0

    res.to_csv("news_duplicates.csv", sep='\t')
    for idx, row in res[::-1].iterrows():
        if idx > 0 and (res.iloc[idx - 1]['date'] == res.iloc[idx]['date']) and (
                res.iloc[idx - 1]['username'] == res.iloc[idx]['username']):
            deleted += news_collection.delete_one({'_id': ObjectId(row["id"])}).deleted_count
            cnt += 1
            print(str(row["id"]), res.iloc[idx - 1]['date'], res.iloc[idx]['date'], res.iloc[idx - 1]['username'],
                  res.iloc[idx]['username'])
    print(f"{cnt} found {deleted} deleted")


def remove_channel_duplicates():
    news_collection = client.trading['tg_channels']

    df_list = []
    for item in news_collection.find():
        df_list.append([item['_id'], item['title']])

    res = pd.DataFrame(df_list, columns=['id', 'title'])
    res.sort_values(['title'], inplace=True)
    res = res.reset_index(drop=True)

    cnt, deleted = 0, 0
    for idx, row in res[::-1].iterrows():
        if idx > 0 and (res.iloc[idx - 1]['title'] == res.iloc[idx]['title']):
            deleted += news_collection.delete_one({'_id': ObjectId(row["id"])}).deleted_count
            cnt += 1
            print(str(row["id"]), res.iloc[idx - 1]['title'], res.iloc[idx]['title'])
    print(f"{cnt} found {deleted} deleted")


#renumerate_channels()
#instrument_collection = client.trading['tg_channels']
#for item in instrument_collection.find({}):
#    instrument_collection.update_one(item, {'$set': {'tags': []}})


# CHANNELS
#"AK47pfl", "ProfitGateClub"
#activate_all_channels(1)#, "cbrstocks")
#print(get_active_channels())
#update_tg_msg_count("cbrstocks",45510)

#news = get_news_from_channels("ProfitGateClub")
#print(len(news), news[0] )

# INSTRUMENT TAGS
#add_tag_word('SiM3', 'сипи')
#remove_tag_word('BRK3', 'brenr')
#get_instrument('RIM3')

# GENERAL
#remove_field('news','is_active')
@sync_timed()
def remove_empty_tag_news():
    news_collection = client.trading['news']

    for item in news_collection.find({}):
        if 'tags' not in item or len(item['tags']) == 0:
            news_collection.delete_one(item)


def remove_security(ticker):
    instrument_collection = client.trading['trading']
    for item in instrument_collection.find({}):
        if item['ticker'] == ticker:
            instrument_collection.delete_one(item)


def insert_security(ticker: str, name: str, namee: List[str]):
    instrument_collection = client.trading['trading']

    if len(list(instrument_collection.find({'ticker': ticker}))) == 0:
        new_item = dict()
        new_item['ticker'] = ticker
        new_item['name'] = name
        new_item['namee'] = namee
        instrument_collection.insert_one(new_item)


def compare_securities_mongo_postgres():
    set_mongo = set()
    set_postgres = set()
    instrument_collection = client.trading['trading']
    for item in instrument_collection.find({}):
        set_mongo.add(item['ticker'])

    items = sql.get_table.query_to_list("select code from secquotes")
    for item in items:
        set_postgres.add(item['code'])

    print("in mongo not in postgres", set_mongo - set_postgres)
    print("in postgres not in mongo", set_postgres - set_mongo)


def clean_old_news(days=90):
    from_date = datetime.datetime.today() - datetime.timedelta(days=days)
    news_collection = client.trading['news']
    query = {"date": {"$lt": from_date}}
    x = news_collection.delete_many(query)
    logger.info(f"{x.deleted_count} documents deleted.")


def clean_mongo():
    """
    clean_old_news(days=90), remove_news_duplicates(), remove_empty_tag_news()
    :return:
    """
    clean_old_news(days=90)
    remove_news_duplicates()
    remove_empty_tag_news()


def channel_stats():
    channel_collection = client.trading['tg_channels']
    news_collection = client.trading['news']
    df_list = []
    for channel in channel_collection.find():
        username = channel['username']
        isactive = channel['is_active']
        title = channel['title']
        description = channel['description'].replace('\n', '')
        members_count = channel['members_count']

        query = {'channel_username': username}
        cnt = 0
        date = None
        for news_item in news_collection.find(query):
            cnt += 1
            date = news_item['date'] if date is None else max(date, news_item['date'])
        df_list.append([username, isactive, cnt, date, title, members_count, description])



    res = pd.DataFrame(df_list,
                       columns=['username', 'isactive', 'cnt', 'date', 'title', 'members_count', 'description'])
    res = res.reset_index(drop=True)
    res.to_csv("channel_stats.csv", sep='\t')


@sync_timed()
def news_tfidf():
    names_collection = client.trading['trading']
    news_collection = client.trading['news']

    # Создаем defaultdict с пустым списком в качестве значения по умолчанию
    news_items = defaultdict(list)

    for document in names_collection.find():
        for item in news_collection.find({"tags": f"{document['ticker']}"}):
            filt = [x for x in item['tags'] if not x[-1].isdigit()]
            news_items[item['date'].date()].append(" ".join(filt))

    def calc_tfidf(documents, date):
        # Создаем экземпляр TfidfVectorizer
        vectorizer = TfidfVectorizer()

        # Обучаем векторайзер и трансформируем документы в TF-IDF вектора
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Получаем имена признаков (слова)
        feature_names = vectorizer.get_feature_names_out()

        # Создаем DataFrame из TF-IDF матрицы
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names,
                                index=[f"Документ {i + 1}" for i in range(len(documents))])

        # Суммируем значения TF-IDF по каждому слову во всех документах
        tfidf_sum = tfidf_df.sum(axis=0)

        # Подсчитываем количество документов, в которых встречается каждое слово
        doc_count = (tfidf_df > 0).sum(axis=0)

        # Создаем итоговый DataFrame для суммы TF-IDF значений и добавляем дополнительную статистику
        tfidf_summary_df = pd.DataFrame({
            'ticker': feature_names,
            'tfidfsum': tfidf_sum,
            'total_daily': len(documents),
            'total_with_ticker': doc_count,
            'date': date
        })
        return tfidf_summary_df

    res = pd.DataFrame()
    for k, v in news_items.items():
        df = calc_tfidf(v, k)
        res = pd.concat([res, df])

    sql.get_table.exec_query("TRUNCATE TABLE public.news_tfidf")
    res.to_sql('news_tfidf', sql.get_table.engine, if_exists='append', index=False)
    #sql.get_table.df_to_sql(res, 'news_tfidf')


if __name__ == "__main__":
    pass
    mylist = ['YNM3',
              'RIM3',
              'GZM3',
              'SNM3',
              'MXM3',
              'RNM3',
              'SFM3',
              'GDM3',
              'GKM3',
              'NAM3',
              'LKM3',
              'EDM3',
              'NKM3',
              'RMM3',
              'SRM3',
              'NGJ3',
              'VBM3',
              'EuM3',
              'POM3',
              'TTM3',
              'PZM3',
              'NMM3',
              'SiM3',
              'CRM3',
              'FVM3',
              'BRK3',
              'CHM3',
              'MEM3',
              'OZM3',
              'MGM3',
              'MNM3',
              'ALM3',
              ]
    for item in mylist:
        remove_security(item)
    name = 'Вконтакте'
    ticker = 'VKCO'
    namee = ['ВК', 'VK', 'VKCO']
    insert_security(ticker, name, namee)

    mylist2 = [('GAZP', 'ГАЗПРОМ'),
               ('GMKN', 'ГМКНорНик'),
               ('TCSG', 'ТКСХолд'),
               ('SBER', 'Сбербанк'),
               ('LKOH', 'ЛУКОЙЛ'),
               ('AFKS', 'Система'),
               ('NLMK', 'НЛМК'),
               ('PLZL', 'Полюс'),
               ('RUAL', 'РУСАЛ'),
               ('ROSN', 'Роснефть'),
               ('MGNT', 'Магнит'),
               ('YNDX', 'Yandex'),
               ('NVTK', 'Новатэк'),
               ('CHMF', 'СевСт'),
               ('MTLR', 'Мечел'),
               ('VKCO', 'ВК'),
               ('TRNFP', 'Транснф'),
               ('MTSS', 'МТС'),
               ('FLOT', 'Совкомфлот'),
               ('AFLT', 'Аэрофлот'),
               ('MAGN', 'ММК'),
               ('SMLT', 'Самолет'),
               ('SNGSP', 'Сургнфгз'),
               ('VTBR', 'ВТБ'),
               ('SNGS', 'Сургнфгз'),
               ('OZON', 'OZON'),
               ('EUTR', 'ЕвроТранс'),
               ('MOEX', 'МосБиржа'),
               ('UGLD', 'ЮГК'),
               ('PHOR', 'ФосАгро'),
               ('ALRS', 'АЛРОСА'),
               ('RNFT', 'РуссНфт'),
               ('POSI', 'Позитив'),
               ('RTKM', 'Ростел'),
               ('TATN', 'Татнфт'),
               ('PIKK', 'ПИК'),
               ('BSPB', 'БСП'),
               ('SBERP', 'Сбербанк'),
               ('LSRG', 'ЛСР'),
               ('BELU', 'НоваБев'),
               ('SIBN', 'Газпрнефть'),
               ('SGZH', 'Сегежа'),
               ('IRAO', 'ИнтерРАОао'),
               ('BANEP', 'Башнефт'),
               ('TRMK', 'ТМК'),
               ('ASTR', 'Астра'),
               ('SOFL', 'Софтлайн'),
               ('SVCB', 'Совкомбанк'),
               ('SPBE', 'СПББиржа'),
               ('ENPG', 'ЭН+ГРУП'),
               ('MTLRP', 'Мечел'),
               ('RTKMP', 'Ростел'),
               ('SVAV', 'СОЛЛЕРС'),
               ('SFIN', 'ЭсЭфАй'),
               ('BANE', 'Башнефт'),
               ('MBNK', 'МТСБанк'),
               ('FEES', 'Россети'),
               ('UPRO', 'Юнипро'),
               ('GLTR', 'GLTR'),
               ('TATNP', 'Татнфт'),
               ('AGRO', 'AGRO'),
               ('LSNGP', 'РСетиЛЭ'),
               ('MVID', 'МВидео'),
               ('UNAC', 'АвиастКао'),
               ('NMTP', 'НМТП'),
               ('HNFG', 'ХЭНДЕРСОН'),
               ('FESH', 'ДВМП'),
               ('SELG', 'Селигдар'),
               ('TGKN', 'ТГК'),
               ('POLY', 'Polymetal'),
               ('LEAS', 'Европлан'),
               ('PMSB', 'ПермьЭнСб'),
               ('WUSH', 'ВУШХолднг'),
               ('DELI', 'Каршеринг'),
               ]
    for item in mylist2:
        ticker = item[0]
        name = item[1]
        namee = [ticker, name]
        insert_security(ticker, name, namee)

    compare_securities_mongo_postgres()
    get_ticker_tags().to_csv('tickertags.csv', sep='\t')
