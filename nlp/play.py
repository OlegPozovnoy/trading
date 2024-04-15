from nlp.mongo_tools import deactivate_channel, channel_stats


def deactivate_routine():
    deact_list = [
        'GBEanalytix'
        , 'yivashchenko'
        , 'invest_fynbos'
        , 'ltrinvestment'
        , 'rynok_znania'
        , 'INVESTR_RU'
        , 'Sharqtradein'
        , 'Rusbafet_vip'
        , 'trekinvest'
    ]

    for item in deact_list:
        deactivate_channel(item)


channel_stats()


#remove_channel('promsvyaz_am')
#remove_channel_duplicates()
#remove_news_duplicates()

#add_tag_channel({"title":"MarketTwits"}, "urgent")
#clean_mongo()
