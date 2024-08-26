import logging
import re
import pymorphy2

from nlp import client

from tools.utils import sync_timed
import ahocorasick

morph = pymorphy2.MorphAnalyzer()

keywords = None
keywords_casesensitive=None
A = None
A_casesensitive = None


A_important = ahocorasick.Automaton(ahocorasick.STORE_LENGTH)
important_words = ['совет директоров', 'дивиденд', 'суд', 'отчетность', 'СД']
for word in important_words:
    A_important.add_word(word)
A_important.make_automaton()


@sync_timed()
def update_importance():
    names_collection = client.trading['news']
    for document in names_collection.find():
        is_important = check_doc_importance(document)
        names_collection.update_one(document, {'$set': {'is_important': is_important}})


#@sync_timed()
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


#@sync_timed()
def load_keywords():
    """заполняем огромный словарь keyword[форма слова] = тикер"""
    global keywords
    global keywords_casesensitive
    global A
    global A_casesensitive
    if keywords is None:
        names_collection = client.trading['trading']
        keywords = dict()
        keywords_casesensitive = dict()

        for document in names_collection.find():
            for x in document['namee']:
                if x[0] == '+':
                    keywords_casesensitive.setdefault(x[1:], []).append(document['ticker'])
                else:
                    x = x.lower()
                    for form in get_words_prononse(x):
                        keywords.setdefault(form, []).append(document['ticker'])
        A = ahocorasick.Automaton()
        for key, values in keywords.items():
            A.add_word(key, values)
        A.make_automaton()

        A_casesensitive = ahocorasick.Automaton()
        for key, values in keywords_casesensitive.items():
            A_casesensitive.add_word(key, values)
        A_casesensitive.make_automaton()
    return keywords, A, keywords_casesensitive, A_casesensitive


@sync_timed()
def build_news_tags(text):
    keywords, A, keywords_casesensitive, A_casesensitive = load_keywords()
    tags = set()
    # сначала не casesensitive
    for end_index, values in A_casesensitive.iter(text):
        tags.update(values)

    # потом переводим в нижний регистр и чистим
    text = preprocess_sentence(text)
    for end_index, values in A.iter(text):
        tags.update(values)

    logging.info(f"build_news_tags returned {list(tags)}")
    return list(tags)


@sync_timed()
def convert_normal_form(sentence):
    return ' '.join([morph.parse(word)[0].normal_form for word in sentence.split()])


#@sync_timed()
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


#@sync_timed()
def get_words_prononse(name):
    # print(morph.parse(name))
    result = []
    for item in name.split():
        word = morph.parse(item)[0]

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
        result.append([x.word if x is not None else 'ERROR' for x in inflect_list] + [item])

    return set([" ".join(t) for t in zip(*result)])

if __name__ == '__main__':
    tags = build_news_tags("""Решил  (https://sun9-42.userapi.com/impg/sBSRX8Q3RSUHiVS1bYUhMGdDI9kZNO5lyo3QLg/0VOLY5ayxN0.jpg?size=957x840&quality=96&sign=36d11b6d036687691aad56fbf8ec913e&type=album)пройтись немного по убыткам за год.

Ladimir Semenov (https://smart-lab.ru/mobile/topic/1021653/) пишет:

В целом дата ничем не примечательна, просто есть энергия и желание на эти размышления. В целом 12 месяцев были отменными.

Наверное возьму отсечение даже в 100к, т.к. в целом позиций не так уж много. Рынок был довольно халявным, а то что я насобирал убытков — мой особый навык влезть куда то плохо подумав. Впрочем так у меня работает мыслительный процесс.

Круче всех — Алибаба. Размер заморозки писать не буду, это дцать миллионов. Помимо этого — там еще и переоценка пакета вниз, шесть нулей — но цифра мало важна когда заморожен весь пакет.

Факт заморозки — это большая часть убытков с большим отрывом. Хотя мб есть какие-то надежды. Мне бы хотелось :)

Дальше идет Башнефть, 2,4 млн. Как так? Ну так… Вот прям щас набрал. Много. На хаях, оно падает… Дивы чот не обещает. Ну, такие дела. Мало сомнений что я здесь таки возьму прибыль, хотя ничто не факт.

МТС… Брал спекульнуть. Все как то припало, и я решил переместиться в другое. Ранней весной было. 2,2

Самый тупой бред — Кармани, лютый неликвид. 1,7 Очень долго выходил… Объемы не але. Имел глупость набрать таки объем. Очередное напоминание что лезть в неликвид — так себе план.

На этом в общем миллионники закончились.

ТМК — 900к, хотелось результатов получше, и следовательно выше дивы — но нет. Не достаточно хорошо капнул. Тут еще стоимость плеча значительна, позиция была больше квартала у меня. С учетом стоимости денег — это шесть нулей.

Росбанк — я даже не помню что я там делал) 700

Преф Ростела — 400, локти кусаю, там должна была быть прибыль миллионы. На общем откате решил подрезать плечи… И не откупил.

NIO 400 — Это я просто спекулил пока спб биржа была. Интрадей.

ОФЗ 400 — Ну, купил, продал дешевле. топ трейдер — потерял денег на офз!)

Суммарно на фьючах ММВБ (MОEX) — 400 тоже (разные периоды прибыль и убыток)

Совкомфлот 400 — не стал дожидаться дивов, переложил деньги куда то..

НЛМК — 350, не дождался рекома дивов

ММВБ 200 — я не помню что там забыл.

Нефть 200 — не помню что там забыл 2.

Деньги, просто плата за плечо. Это меньше чем заморозка, но больше любого убытка от биржевой цены. В разы. Но плечи за этот период однозначно окупились с лихвой.

Пишите свои мысли в комментарии:
https://smart-lab.ru/mobile/topic/1021653

""")
    print(tags)

    print(get_words_prononse("Yandex"))
# update_all_tags()
# print(load_keywords())
# get_words_prononse("ММК")
# get_words_prononse("ВТБ")
# update_importance()
