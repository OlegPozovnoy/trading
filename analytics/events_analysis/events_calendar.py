from datetime import datetime

import pandas as pd

from nlp.lang_models import build_news_tags

df_rcb = pd.read_csv('rcb_filtered_news.csv', sep = '\t')
df_markettwits = pd.read_csv('markettwits_filtered_news.csv', sep = '\t')

df = pd.concat([df_rcb, df_markettwits], axis=0)

print(len(df), df.head())


new_list = []

for _, item in df.iterrows():
    for tag in  build_news_tags(item['text']):
        dt = pd.to_datetime(item['date'], format='mixed')
        new_list.append([tag, item['date'], item['text'], item['tag'], item['source'], datetime(year=2024, month=dt.month, day=dt.day)])

new_df = pd.DataFrame(new_list, columns = ['ticker', 'date', 'text', 'news_tag' ,'source', 'adjusted_date'])

new_df.to_csv('news_calendar.csv', sep = '\t')