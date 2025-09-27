from sql.get_table import exec_query
from tools import get_pc_code


# Функция для выполнения запроса через dblink без изменений строки запроса
# Функция для выполнения запроса через dblink без изменений строки запроса
# Функция для выполнения запроса через dblink без изменений строки запроса
# Функция для выполнения запроса через dblink без изменений строки запроса
# Функция для выполнения запроса через dblink без изменений строки запроса
# Функция для выполнения запроса через dblink без изменений строки запроса
def exec_remote_dblink(query):
    # Формирование запроса с использованием dblink и параметров
    dblink_connection_str = "dbname=test host=10.8.0.3 user=postgres password=postgres"
    dblink_query = f"SELECT dblink_exec('{dblink_connection_str}', $$ {query} $$);"

    # Выполнение запроса через dblink
    return exec_query(dblink_query)


print(get_pc_code())
