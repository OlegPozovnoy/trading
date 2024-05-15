import logging
import re
import pymorphy2

from nlp import client
from datetime import datetime, timedelta

from tools.utils import sync_timed
from numba import njit
import ahocorasick

morph = pymorphy2.MorphAnalyzer()

keywords = None
A = None

A_important = ahocorasick.Automaton()
important_words = ['совет директоров', 'дивиденд', 'суд', 'отчетность', 'СД']
for word in important_words:
    A_important.add_word(word, word)
A_important.make_automaton()


@sync_timed()
def update_importance():
    names_collection = client.trading['news']
    for document in names_collection.find():
        is_important = check_doc_importance(document)
        names_collection.update_one(document, {'$set': {'is_important': is_important}})


@sync_timed()
def check_doc_importance(document):
    global A_important
    fulltext = str(document['text']) + " " + str(document['caption'])
    #return any(check_sentence(fulltext, word) for word in important_words)
    return len(list(A_important.iter(fulltext))) > 0


@sync_timed()
def update_all_tags():
    names_collection = client.trading['news']

    for document in names_collection.find():
        fulltext = str(document['text']) + " " + str(document['caption'])
        tags = build_news_tags(fulltext)
        names_collection.update_one(document, {'$set': {'tags': tags}})


@sync_timed()
def load_keywords():
    """заполняем огромный словарь keyword[форма слова] = тикер"""
    global keywords
    global A
    if keywords is None:
        names_collection = client.trading['trading']
        keywords = dict()

        for document in names_collection.find():
            for x in document['namee']:
                x = x.lower()
                for form in get_words_prononse(x):
                    keywords.setdefault(form, []).append(document['ticker'])
        A = ahocorasick.Automaton()
        for key, values in keywords.items():
            A.add_word(key, values)
        A.make_automaton()
    return keywords, A


@sync_timed()
def build_news_tags(text):
    keywords, A = load_keywords()
    text = preprocess_sentence(text)
    tags = set()
    for end_index, values in A.iter(text):
        tags.update(values)

    # Обработка многословных ключей в нормализованной форме текста
    normalized_text = ' '.join([morph.parse(word)[0].normal_form for word in text.split()])
    for keyword, values in keywords.items():
        if ' ' in keyword:  # Только многословные ключи
            normal_form_keyword = ' '.join([morph.parse(word)[0].normal_form for word in keyword.split()])
            if normal_form_keyword in normalized_text:
                tags.update(values)
    print(f"{tags =}")
    return list(tags)


@sync_timed()
def convert_normal_form(sentence):
    return ' '.join([morph.parse(word)[0].normal_form for word in sentence.split()])


@sync_timed()
def preprocess_sentence(sentence):
    sentence = sentence.lower().replace('ё', 'е')
    #sentence_split = re.sub(r'[^а-яa-z]+', ' ', sentence).split()
    return " ".join(re.sub(r'[^а-яa-z]+', ' ', sentence).split())


@sync_timed()
def check_sentence(sentence, name):
    english_check = re.compile(r'[a-z]')
    if english_check.match(name) and name in sentence:
        return True
    elif len(name.split()) >= 2:
        return convert_normal_form(name) in convert_normal_form(sentence)
    elif name in sentence:
        return True
    return False


@sync_timed()
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
    return list(set(inflect_list))

# update_all_tags()
# print(load_keywords())
# get_words_prononse("ММК")
# get_words_prononse("ВТБ")
# update_importance()
