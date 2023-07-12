from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd

client = MongoClient()

def activate_all_channels(is_active, username = None):
    names_collection = client.trading['tg_channels']

    filter_str = {} if username is None else {'username':username}

    for document in names_collection.find(filter_str):
        res = names_collection.update_one(document, {'$set': {'is_active': is_active}})
        print(res)

def remove_field(db, field_name):
    names_collection = client.trading[db]
    names_collection.update_many({}, {'$unset': {f'{field_name}': ''}}, False)


def remove_channel(channel_name):
    news_collection = client.trading['news']
    channels_collection = client.trading['tg_channels']

    news_filter = {'channel_username':channel_name}
    tg_filter = {'username': channel_name}

    for item in news_collection.find(news_filter):
        print(item)
        news_collection.delete_one(item)

    for item in channels_collection.find(tg_filter):
        print(item)
        channels_collection.delete_one(item)


def get_active_channels():
    names_collection = client.trading['tg_channels']
    result = []
    for document in names_collection.find({'is_active': 1}):
        result.append(document)
    return result


def get_news_from_channels(username):
    names_collection = client.trading['news']
    result = []#channel_title 'channel_username':

    for document in names_collection.find({'channel_username': username}):
        result.append(document)
    return result


def update_tg_msg_count(username, count):
    names_collection = client.trading['tg_channels']
    names_collection.update_one({'username': username}, {'$set': {'count': count}})
    print(names_collection.find_one({'username': username}))


def remove_tag_word(ticker, tag):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    print(set(instrument['namee']),set([tag]))
    new_tags = list(set(instrument['namee']) - set([tag]))
    print(instrument, "->", new_tags)
    instrument_collection.update_one({'ticker': ticker}, {'$set': {'namee': new_tags}})


def add_tag_word(ticker, tag):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    new_tags =set(instrument['namee'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'ticker': ticker}, {'$set': {'namee': list(new_tags)}})

def get_instrument(ticker):
    instrument_collection = client.trading['trading']
    instrument = instrument_collection.find_one({'ticker': ticker})
    print(instrument)


def add_tag_channel(query, tag):
    instrument_collection = client.trading['tg_channels']
    instrument = instrument_collection.find_one(query)
    if 'tags' not in instrument: instrument['tags'] = []
    new_tags =set(instrument['tags'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'_id':instrument['_id']}, {'$set': {'tags': list(new_tags)}})


def remove_tag_channel(query, tag):
    instrument_collection = client.trading['tg_channels']
    instrument = instrument_collection.find_one(query)
    new_tags =set(instrument['tags'])
    new_tags.add(tag)
    print(instrument, new_tags)
    instrument_collection.update_one({'_id':instrument['_id']}, {'$set': {'tags': list(new_tags)}})



def renumerate_channels(is_active=False):
    out_id=0
    instrument_collection = client.trading['tg_channels']

    query = {"is_active": 1} if is_active else {}

    for item in instrument_collection.find(query):
        out_id += 1
        instrument_collection.update_one(item, {'$set': {'out_id': out_id}})


def remove_news_duplicates():
    news_collection = client.trading['news']

    res = pd.DataFrame()

    for item in news_collection.find():
        add = pd.DataFrame({'id': item['_id'], 'date': item['date'], 'username': item['channel_username']}, index=[0])
        res = pd.concat([res, add])

    res.sort_values(['date', 'username'], inplace=True)
    res = res.reset_index(drop=True)

    cnt, deleted = 0, 0
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

    res = pd.DataFrame()

    for item in news_collection.find():
        add = pd.DataFrame({'id': item['_id'], 'title': item['title']}, index=[0])
        res = pd.concat([res, add])

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

def remove_empty_tag_news():
    news_collection = client.trading['news']

    for item in news_collection.find({}):
            if len(item['tags']) == 0:
                news_collection.delete_one(item)

remove_news_duplicates()
remove_empty_tag_news()
#remove_channel('promsvyaz_am')
#remove_channel_duplicates()
#remove_news_duplicates()


#add_tag_channel({"title":"MarketTwits"}, "urgent")