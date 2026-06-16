import logging
import os
from pathlib import Path
import subprocess
import sys
from dotenv import load_dotenv, find_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters

from telegrambot.queries import get_orders, place_order, invert_state
import tools.clean_processes

#logger = logging.getLogger()
logger = logging.getLogger("tgbot")
logger.setLevel(logging.INFO)

BASE_DIR = Path(__file__).resolve().parents[1]
logger.info(BASE_DIR)

load_dotenv(find_dotenv('my.env', raise_error_if_not_found=True))
TOKEN = os.getenv('tg_key')

USE_PROXY = os.environ.get("use_proxy") == "True"

TG_PROXY_URL = (
    f"{os.environ.get('tg_proxy_scheme', 'socks5')}://"
    f"{os.environ.get('tg_proxy_host', '127.0.0.1')}:"
    f"{int(os.environ.get('tg_proxy_port', '1088'))}"
)

ROOT, GET_CHOICE, UPDATE_CHOICE = range(3)

reply_keyboard = [["code", "quantity", "state"],
                  ["barrier_up", "max_amount", "pause"],
                  ["provider", "barrier_down", "order_nums"],
                  ["get_orders", "invert_state", "place_order"],
                  ["send_news"]]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]


def init_user_data(context: ContextTypes.DEFAULT_TYPE) -> ContextTypes.DEFAULT_TYPE:
    context.user_data['code'] = 'MXM4'
    context.user_data['quantity'] = 0
    context.user_data['state'] = 1

    context.user_data['barrier_up'] = "None"
    context.user_data['max_amount'] = 1
    context.user_data['pause'] = 10

    context.user_data['provider'] = "None"
    context.user_data['barrier_down'] = "None"
    context.user_data['order_nums'] = 10
    return context


async def root(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their preferred car type."""
    if update.effective_user.id == 40361390:
        if 'code' not in context.user_data:
            context = init_user_data(context)
        else:
            context = process_context(update.message.text, context)

        msg = f"root {update.message.text}\n{context.user_data}\n"

        if update.message.text == 'get_orders':
            result = get_orders()
            await update.get_bot().send_message(update.effective_chat.id, result,
                                                reply_markup=reply_markup, parse_mode='HTML')
        elif update.message.text == 'place_order':
            result = place_order(context.user_data)
            await update.get_bot().send_message(update.effective_chat.id, result,
                                                reply_markup=reply_markup, parse_mode='HTML')
        elif update.message.text == 'send_news':
            script_path = BASE_DIR / "analytics" / "important_news.py"
            try:
                logger.info("Launching important_news script: %s", script_path)
                subprocess.Popen([sys.executable, str(script_path)])
                text = "Запустил important_news.py, новости должны прийти тебе на почту."
            except Exception as e:
                logger.exception("Failed to launch important_news.py: %s", e)
                text = "Не смог запустить important_news.py, смотри лог."

            await update.get_bot().send_message(
                update.effective_chat.id,
                text,
                reply_markup=reply_markup,
            )

        await update.message.reply_text(msg, reply_markup=reply_markup)
        return GET_CHOICE
    else:
        await update.message.reply_text("Поцелуй моего ишака под хвост")
        return ConversationHandler.END


def process_context(value: str, context: ContextTypes.DEFAULT_TYPE) -> ContextTypes.DEFAULT_TYPE:
    try:
        if 'updated_field' in context.user_data:
            field = context.user_data['updated_field']
            if field == 'code':
                context.user_data[field] = value.upper()
            elif field in ['quantity', 'state', 'max_amount', 'pause', 'order_nums']:
                context.user_data[field] = int(value)
            elif field in ['barrier_up', 'barrier_down']:
                context.user_data[field] = None if value == "None" else float(value)
            elif field == 'provider':
                context.user_data[field] = None if value == "None" else value
            elif field == 'invert_state':
                invert_state(int(value))
            del context.user_data['updated_field']
    except Exception as e:
        logger.error(str(e))
    finally:
        return context


async def regular_choice(update, context):
    msg = f"regular_choice {update.message.text}\n"
    temp_keyboard = None
    if update.message.text == 'code':
        pass
    elif update.message.text == 'quantity':
        pass
    elif update.message.text == 'state':
        temp_keyboard = [["0", "1"]]
    elif update.message.text == 'max_amount':
        temp_keyboard = [["1", "10"]]
    elif update.message.text == 'pause':
        temp_keyboard = [["1", "5", "10"]]
    elif update.message.text == 'provider':
        temp_keyboard = [["None", "tcs"]]
    elif update.message.text == 'barrier_up':
        temp_keyboard = [["None"]]
    elif update.message.text == 'barrier_down':
        temp_keyboard = [["None"]]
    elif update.message.text == 'order_nums':
        temp_keyboard = [["1", "10"]]
    elif update.message.text == 'invert_state':
        pass
    else:
        await update.message.reply_text(msg + f"Не понял, введите что-нибудь")
        return ROOT

    context.user_data['updated_field'] = update.message.text
    msg = msg + f"Введите новое значение {update.message.text}"
    if temp_keyboard:
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(temp_keyboard, one_time_keyboard=True))
    else:
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[]]))
    return ROOT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Странная ошибка, Уотсон. До завтра!')
    return ConversationHandler.END


def main():
    builder = Application.builder().token(TOKEN)

    if USE_PROXY:
        builder = builder.proxy(TG_PROXY_URL).get_updates_proxy(TG_PROXY_URL)

    application = builder.build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', root),
            MessageHandler(filters.TEXT & ~filters.COMMAND, root)  # Обработчик текстовых сообщений
        ],
        states={
            ROOT: [MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=root)],
            GET_CHOICE: [
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND & ~filters.Regex('^(get_orders|place_order|send_news)$'),
                               callback=regular_choice),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND & filters.Regex('^(get_orders|place_order|send_news)$'),
                               callback=root)
            ],  #
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    if not tools.clean_processes.clean_proc("tgbot", os.getpid(), 999999):
        print("something is already running")
        exit(0)

    main()
