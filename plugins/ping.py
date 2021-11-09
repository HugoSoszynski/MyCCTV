from typing import Dict
from plugin import Plugin
from telegram import Update
from telegram.ext import CallbackContext


class Ping(Plugin):

    @staticmethod
    def hooks() -> Dict[str, object]:
        return {
            "ping": Ping.ping
        }

    @staticmethod
    def ping(update: Update, context: CallbackContext) -> None:
        """Sends a \"Pong\" message"""
        update.message.reply_text('Pong')

