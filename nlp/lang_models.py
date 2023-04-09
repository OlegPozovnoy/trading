import logging
import re
import pymorphy2


from pymongo import MongoClient
from datetime import datetime, timedelta


client = MongoClient()
morph = pymorphy2.MorphAnalyzer()



def update_all_tags():
    names_collection = client.trading['news']

    for document in names_collection.find():
        fulltext = str(document['text'])+" "+ str(document['caption'])
        tags = build_news_tags(fulltext)
        names_collection.update_one(document, {'$set': {'tags': tags}})


def load_keywords():
    names_collection = client.trading['trading']
    keywords = dict()

    for document in names_collection.find():
        for x in document['namee']:
            keywords[x] = document['ticker']
    return keywords

def build_news_tags(text):
    keywords = load_keywords()
    tags = []
    for key, value in keywords.items():
        if check_sentence(text, key):
            tags.append(value)

    return list(set(tags))



def check_sentence(sentence, name):
    global morph
    sentence = sentence.lower()
    sentence_split = re.sub(r'[^а-яa-z]+', ' ', sentence).split()

    name = name.lower()
    english_check = re.compile(r'[a-z]')
    if english_check.match(name) and sentence.find(name) > 0:
        return True
    else:
        inflect_list = get_words_prononse(name)

        for item in inflect_list:
            if item in sentence_split:
                return True

    return False


def get_words_prononse(name):
    print(morph.parse(name))
    word = morph.parse(name)[0]

    inflect_list = [
        word.inflect({'nomn'}),
        word.inflect({'gent'}),
        word.inflect({'datv'}),
        word.inflect({'accs'}),
        word.inflect({'ablt'}),
        word.inflect({'loct'}),
        word.inflect({'nomn', 'plur'}),
        word.inflect({'gent', 'plur'}),
        word.inflect({'datv', 'plur'}),
        word.inflect({'accs', 'plur'}),
        word.inflect({'ablt', 'plur'}),
        word.inflect({'loct', 'plur'})
    ]

    inflect_list = [x.word for x in inflect_list if x is not None]
    print(f"{name}: {inflect_list}")
    return list(set(inflect_list))


update_all_tags()
#print(load_keywords())
#get_words_prononse("ВТБ")


#Если с большой буквы -  убираем все не с большой, если с маленькой - смотрим все слова