#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import re
from dbSigesmen import Database
import json
import time
import unicodedata


MSG_OK = "Mensaje al código {0} envíado correctamente"
BAD_CODE = "Códgo {0} no pertenece a nuestra base de datos"
BAD_MSG = "Mensaje incorrecto. Recuerde que es clave o código y luego el mensaje."
MSG_FROM_TELEGRAM = "Enviado desde Telegram."

REGULAR_EXP = r"\d{4}"
DATABASE_FILE = "dbConf.json"
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open(DATABASE_FILE) as db:
    configFile = json.load(db)
db = Database(configFile["user"], configFile["passwd"], configFile["host"], configFile["port"], configFile["database"])

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    newMsg = ''.join(c for c in unicodedata.normalize('NFD', update.message.text.strip()) if unicodedata.category(c) != 'Mn')
    newMsg.encode('ascii', 'ignore').decode('ascii')
    match = re.match(REGULAR_EXP, newMsg)
    if match:
        code = match.group()
        message = re.sub(code, '', newMsg)

        if db.isCodeExists(code):
            msgId = db.sendMessage(code, "{0}. {1}".format(message, MSG_FROM_TELEGRAM))
            update.message.reply_text(MSG_OK.format(code))
        else:
            update.message.reply_text(BAD_CODE.format(code))
    else:
        update.message.reply_text(BAD_MSG)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("412565617:AAFPbyHRCXbOZG7DjUTmNeeQyApnxabJ35k")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()