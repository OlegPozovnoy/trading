from nlp import client
from nlp.mongo_tools import deactivate_channel, channel_stats

# remove_channel('promsvyaz_am')
# remove_channel_duplicates()
# remove_news_duplicates()

# add_tag_channel({"title":"MarketTwits"}, "urgent")
# clean_mongo()


names_collection = client.trading['trading']
news_collection = client.trading['news']

for document in names_collection.find():
    cnt = 0
    for item in news_collection.find({"tags": f"{document['ticker']}"}):
        cnt += 1/len(item['tags'])
        if document['ticker'] == 'MEM3':
            print(item)

    print(document['ticker'], cnt)
