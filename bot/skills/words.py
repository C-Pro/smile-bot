import logging
from datetime import datetime
from typing import List

import pymongo
import telegram
from pymongo.collection import Collection
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, run_async, CommandHandler

from db.mongo import get_db
from filters import admin_filter
from mode import cleanup_update_context

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, db_name: str):
        self._coll: Collection = get_db(db_name).words

    def add_word(self, word: str):
        self._coll.update_one({"word": word}, {
            "$inc": {"count": 1},
            "$set": {"last_use": datetime.now()}
        }, upsert=True)

    def add_words(self, words: List[str]):
        for word in words:
            self.add_word(word)

    def find_all(self):
        return self._coll.find({}).sort("count", pymongo.DESCENDING)


_db = DB(db_name='words')


def add_words(upd: Updater, handlers_group: int):
    logger.info("register words handlers")
    dp = upd.dispatcher
    dp.add_handler(CommandHandler("top", show_top, filters=admin_filter), handlers_group)
    dp.add_handler(MessageHandler(Filters.text, extract_words), handlers_group)


@run_async
def extract_words(update: Update, context: CallbackContext):
    _db.add_words(_normalize(_get_words(update.message.text)))


def _get_words(t: str) -> List[str]:
    return t.split(' ')


def _normalize(words: List[str]) -> List[str]:
    return [w.lower() for w in words if w[0] != '/']


@run_async
@cleanup_update_context(seconds=600, remove_cmd=True, remove_reply=True)
def show_top(update: Update, context: CallbackContext):
    _top_limit = 10
    # TODO: make it pretty
    top = "\n".join([f"{w['word']}: {w['count']}" for w in list(_db.find_all())[:_top_limit]])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"```\n{top}\n```", disable_notification=True,
                             parse_mode=telegram.ParseMode.MARKDOWN)