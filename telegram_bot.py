import datetime
import os
from importlib import import_module
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

from setting import TOKEN, PLUGINS, PLUGINS_DIRECTORY


HELP_MESSAGES = {}


def help(update: Update, context: CallbackContext) -> None:
    msg = 'Help of the available commands:\n'
    for cmd, help in HELP_MESSAGES.items():
        msg += '\n' + cmd + '\t' + help
    update.message.reply_text(msg)


def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Pong')


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('ping', ping))

    for plugin in PLUGINS:
        m = import_module(PLUGINS_DIRECTORY + '.' + plugin)
        p = getattr(m, plugin.capitalize())
        for hook, fun in p.hooks().items():
            c_name = plugin + '_' + hook
            HELP_MESSAGES[c_name] = fun.__doc__
            dp.add_handler(CommandHandler(c_name, fun))

    updater.start_polling()
    updater.idle()