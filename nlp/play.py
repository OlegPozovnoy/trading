import sql.get_table
from nlp import client
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from collections import defaultdict

from nlp.mongo_tools import news_tfidf, remove_news_duplicates, remove_empty_tag_news

# remove_channel('promsvyaz_am')
# remove_channel_duplicates()
# remove_news_duplicates()

# add_tag_channel({"title":"MarketTwits"}, "urgent")
# clean_mongo()


news_tfidf()
