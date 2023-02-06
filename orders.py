import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="testload",
    user="haki",
    password=None,
)
connection.autocommit = True

with connection.cursor() as cursor:
    print(cursor)

# KILL_ACTIVE_ORDERS 	- 	Признак снятия активных заявок по данному инструменту. Используется только при «ACTION» =
# «NEW_QUOTE». Возможные значения: «YES» или «NO»

#CLASSCODE 	- 	Код класса, по которому выполняется транзакция, например TQBR. Обязательный параметр
#SECCODE 	- 	Код инструмента, по которому выполняется транзакция, например SBER
#ACTION 	- 	Вид транзакции, имеющий одно из следующих значений:

#«NEW_ORDER» – новая заявка,
#«NEW_STOP_ORDER» – новая стоп-заявка,
#«KILL_ORDER» – снять заявку,
#«KILL_STOP_ORDER» – снять стоп-заявку,
#«KILL_ALL_ORDERS» – снять все заявки из торговой системы,
#«KILL_ALL_STOP_ORDERS» – снять все стоп-заявки,
#«KILL_ALL_FUTURES_ORDERS» – снять все заявки на рынке FORTS,
#«MOVE_ORDERS» – переставить заявки на рынке FORTS,
#«NEW_QUOTE» – новая безадресная заявка,
#«KILL_QUOTE» – снять безадресную заявку,
