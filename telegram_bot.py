import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

from setting import TOKEN, UPDATE_RATE, IMAGES_DIR


def ping(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Pong')

#
# Here are the command that manage the check of a directory containing photos
# sending them to me and moving them to another directory for rotation.
#


def send_image(path: str, context: CallbackContext, caption=None) -> None:
    """Send an image message"""
    if not caption:
        caption = str(datetime.datetime.now())

    job = context.job
    context.bot.send_photo(
        job.context,
        photo=open(path, 'rb'),
        caption=caption
    )


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def alarm(context: CallbackContext) -> None:
    """Sends the newly available images"""
    for filename in os.listdir(IMAGES_DIR):
        file = os.path.join(IMAGES_DIR, filename)
        if os.path.isfile(file) and file.endswith('.png'):
            send_image(file, context)
            os.unlink(file)


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id

    due = int(UPDATE_RATE)

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_repeating(alarm, due, context=chat_id, name=str(chat_id))

    text = 'Job successfully started!'
    if job_removed:
        text += ' Old one was removed.'
    update.message.reply_text(text)


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Job successfully cancelled!' if job_removed else 'You have no active job.'
    update.message.reply_text(text)


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler("start", set_timer))
    dp.add_handler(CommandHandler("stop", unset))
    updater.start_polling()
    updater.idle()