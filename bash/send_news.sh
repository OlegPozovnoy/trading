#!/bin/bash

# Переход в корень проекта
cd /home/oleg/PycharmProjects/trading/

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем PYTHONPATH, чтобы Python знал о папке sql
export PYTHONPATH=$PYTHONPATH:/home/oleg/PycharmProjects/trading

# Проверяем активное окружение и доступные модули
echo "Python в виртуальном окружении: $(which python)"
echo "Модули в окружении: $(python -m pip freeze)"

# Запускаем скрипт Python
python analytics/important_news.py

# Деактивируем виртуальное окружение
deactivate
