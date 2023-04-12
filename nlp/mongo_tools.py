from pymongo import MongoClient

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


def get_active_channels():
    names_collection = client.trading['tg_channels']
    result = []
    for document in names_collection.find({'is_active':1}):
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


# CHANNELS
#"AK47pfl", "ProfitGateClub"
#activate_all_channels(1, "cbrstocks")
print(get_active_channels())
#update_tg_msg_count("cbrstocks",45510)

#news = get_news_from_channels("ProfitGateClub")
#print(len(news), news[0] )

# INSTRUMENT TAGS
#add_tag_word('SiM3', 'сипи')
#remove_tag_word('BRK3', 'brenr')
#get_instrument('RIM3')

# GENERAL
#remove_field('news','is_active')
