import json
from time import time, ctime
import os.path

import pandas as pd
from QuikPy.QuikPy import QuikPy  # Работа с QUIK из Python через LUA скрипты QuikSharp

import sql.get_table

engine = sql.get_table.engine
qpProvider = None
settings_path = "./Examples/Bars_upd_config.json"

def GetCandlesDF(classCode, secCodes, candles_num=0):
    result_df = pd.DataFrame()
    for secCode in secCodes:  # Пробегаемся по всем тикерам - переделать на таблицы
        try:
            print(secCode)
            newBars = qpProvider.GetCandlesFromDataSource(classCode, secCode, 1, candles_num)[
                "data"]  # Получаем все свечки
            pdBars = pd.DataFrame.from_dict(pd.json_normalize(newBars),
                                            orient='columns')  # Внутренние колонки даты/времени разворачиваем в отдельные колонки
            pdBars.rename(columns={'datetime.year': 'year', 'datetime.month': 'month', 'datetime.day': 'day',
                                   'datetime.hour': 'hour', 'datetime.min': 'minute', 'datetime.sec': 'second'},
                          inplace=True)  # Чтобы получить дату/время переименовываем колонки
            pdBars.index = pd.to_datetime(
                pdBars[['year', 'month', 'day', 'hour', 'minute', 'second']])  # Собираем дату/время из колонок

            pdBars = pdBars[['open', 'close', 'high', 'low', 'volume']]  # Отбираем нужные колонки
            # для скорости используем только close - для нормальных обьемов надо все
            # pdBars = pdBars[['close', 'volume']]
            pdBars.index.name = 'datetime'  # Ставим название индекса даты/времени
            pdBars.volume = pd.to_numeric(pdBars.volume, downcast='integer')  # Объемы могут быть только целыми
            pdBars['security'] = secCode
            pdBars['class_code'] = classCode
            print('records readed:', len(pdBars))
            result_df = pd.concat([result_df, pdBars])
        except Exception as e:
            print(str(e))
            pass
    print(f"columns type: {result_df.dtypes}")
    return result_df


def SaveCandlesToFile(class_sec, fileName, candles_num=0):
    """Получение баров, объединение с имеющимися барами в файле (если есть), сохранение баров в файл
    :param classCode: Код рынка
    :param compression: Кол-во минут для минутного графика. Для остальных = 1
    """

    result_df = pd.DataFrame()
    for classCode, secCodes in class_sec:
        print(f'GetCandlesDF({classCode}, {secCodes}, {candles_num}')
        new_df = GetCandlesDF(classCode, secCodes, candles_num)
        result_df = pd.concat([result_df, new_df])

    isFileExists = os.path.isfile(fileName)  # Существует ли файл
    if (not isFileExists) or os.path.getsize(fileName) < 1000:  # Если файл не существует
        fileBars = pd.DataFrame()
    else:  # Файл существует
        fileBars = pd.read_csv(fileName, sep='\t', index_col='datetime')  # Считываем файл в DataFrame
        fileBars.index = pd.to_datetime(fileBars.index, format='%d.%m.%Y %H:%M')  # Переводим индекс в формат datetime

    print(len(result_df), len(fileBars))
    fileBars = pd.concat([result_df, fileBars]).drop_duplicates(keep='last').sort_index()
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')
    print("saving to DB ", ctime())
    print("saving to file ", ctime())
    fileBars.to_csv(fileName, sep='\t', date_format='%d.%m.%Y %H:%M')

    print("saved", ctime())
    print(f'- В файл {fileName} сохранено записей: {len(fileBars)}')


def update_all_quotes(to_remove=True, candles_num=4100):
    global qpProvider
    fileName = './Data/candles.csv'

    if to_remove:
        try:
            print("removing old file")
            os.remove(fileName)
        except Exception as e:
            print(time())
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

    startTime = time()  # Время начала запуска скрипта

    try:
        qpProvider = QuikPy()  # Вызываем конструктор QuikPy с подключением к локальному компьютеру с QUIK

        with open(settings_path, 'r') as fp:
            settings = json.load(fp)
        SaveCandlesToFile(
            [(settings["equities"]["classCode"], settings["equities"]["secCodes"]),
             (settings["futures"]["classCode"], settings["futures"]["secCodes"])],
            fileName=fileName, candles_num=candles_num)
    finally:
        qpProvider.CloseConnectionAndThread()  # Перед выходом закрываем соединение и поток QuikPy из любого экземпляра
    print(f'04 - Bars_upd выполнен за {(time() - startTime):.2f} с')


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    update_all_quotes(to_remove=False, candles_num=10)
