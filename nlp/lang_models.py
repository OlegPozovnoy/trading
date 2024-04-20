import logging
import re
import pymorphy2

from nlp import client
from datetime import datetime, timedelta

morph = pymorphy2.MorphAnalyzer()

keywords = None

important_words = ['совет директоров', 'дивиденд', 'суд', 'отчетность', 'СД']


def update_importance():
    names_collection = client.trading['news']
    for document in names_collection.find():
        is_important = check_doc_importance(document)
        names_collection.update_one(document, {'$set': {'is_important': is_important}})


def check_doc_importance(document):
    fulltext = str(document['text']) + " " + str(document['caption'])
    if len(document['tags']) > 0:
        for word in important_words:
            if check_sentence(fulltext, word):
                return True
        return False
    return False


def update_all_tags():
    names_collection = client.trading['news']

    for document in names_collection.find():
        fulltext = str(document['text']) + " " + str(document['caption'])
        tags = build_news_tags(fulltext)
        names_collection.update_one(document, {'$set': {'tags': tags}})


def load_keywords():
    global keywords
    if keywords is None:
        names_collection = client.trading['trading']
        keywords = dict()

        for document in names_collection.find():
            for x in document['namee']:
                if x in keywords:
                    keywords[x].extend([document['ticker']])
                else:
                    keywords[x] = [document['ticker']]
    return keywords


def build_news_tags(text):
    keywords = load_keywords()
    tags = []
    for key, value in keywords.items():
        if check_sentence(text, key):
            tags.extend(value)
    return list(set(tags))


def convert_normal_form(sentence):
    res = []
    words = sentence.split()
    for item in words:
        res.append(morph.parse(item)[0].normal_form)
    return ' '.join(res)


def check_sentence(sentence, name):
    global morph
    sentence = sentence.lower()
    sentence = sentence.replace('ё', 'е')
    sentence_split = re.sub(r'[^а-яa-z]+', ' ', sentence).split()

    name = name.lower()
    english_check = re.compile(r'[a-z]')
    if english_check.match(name) and sentence.find(name) > 0:
        return True
    else:
        if len(name.split()) >= 2: return convert_normal_form(name) in convert_normal_form(sentence)

        inflect_list = get_words_prononse(name)

        for item in inflect_list:
            if item in sentence_split:
                return True
    return False


def get_words_prononse(name):
    # print(morph.parse(name))
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

    inflect_list = [x.word for x in inflect_list if x is not None] + [name]
    # print(f"{name}: {inflect_list}")
    return list(set(inflect_list))

# update_all_tags()
# print(load_keywords())
# get_words_prononse("ММК")
# get_words_prononse("ВТБ")
# update_importance()
