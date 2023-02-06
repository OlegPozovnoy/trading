#!/bin/bash
cd "$(dirname $(dirname "$0"))"
source /home/oleg/PycharmProjects/trading/venv/bin/activate
python /home/oleg/PycharmProjects/trading/morning_routine.py
deactivate
