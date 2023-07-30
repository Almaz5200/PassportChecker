from crawler import crawl
from concurrent.futures import ThreadPoolExecutor
import os
import datetime
from telegram import Update
import time
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    Filters,
)
import schedule
import sys
from database import DatabaseStorage

storage = DatabaseStorage()
print("TOKEN", os.environ["TOKEN"])
print("env", os.environ)
updater = Updater(os.environ["TOKEN"])


def reply(update: Update, context: CallbackContext) -> None:
    if not update.message.text.isdigit():
        return
    storage.set_passport_id(str(update.message.from_user.id), update.message.text)


def do_user(user_id: str):
    user = storage.get(user_id)
    result = crawl(user["passport_id"])
    storage.set_info(user_id, result)

    send_message(
        user_id,
        f"📅 {datetime.datetime.now()}\nStatus: {result.status}\nProgress: {result.progress}",
        force=user["status"] != result.status or user["progress"] != result.progress,
    )


def send_message(user_id: str, message: str, force: bool = False):
    message_id = storage.get_message_id(user_id)
    if message_id and not force:
        updater.bot.edit_message_text(
            chat_id=user_id, message_id=message_id, text=message
        )
    else:
        message_id = updater.bot.send_message(chat_id=user_id, text=message).message_id
        storage.set_message_id(user_id, message_id)


def do_users():
    for user_id in storage.get_users_ids():
        do_user(user_id[0])


def main():
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    schedule.every(10).seconds.do(do_users)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(main)
        while True:
            executor.submit(schedule.run_pending())
            time.sleep(1)
