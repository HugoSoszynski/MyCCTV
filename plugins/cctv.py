import os
import subprocess
import sys
from time import sleep
from datetime import datetime
from typing import Dict
from plugin import Plugin
from telegram import Update
from telegram.ext import CallbackContext

from setting import UPDATE_RATE, IMAGES_DIR


_CCTV_PROCESS = None

class Cctv(Plugin):

    @staticmethod
    def hooks() -> Dict[str, object]:
        return {
            "start": Cctv.set_timer,
            "stop": Cctv.unset,
        }

    @staticmethod
    def send_image(path: str, context: CallbackContext, caption=None) -> None:
        """Send an image message"""
        if not caption:
            caption = str(datetime.now())

        job = context.job
        context.bot.send_photo(
            job.context,
            photo=open(path, 'rb'),
            caption=caption
        )

    @staticmethod
    def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    @staticmethod
    def alarm(context: CallbackContext) -> None:
        """Sends the newly available images"""
        for filename in os.listdir(IMAGES_DIR):
            file = os.path.join(IMAGES_DIR, filename)
            if os.path.isfile(file) and file.endswith('.png'):
                Cctv.send_image(file, context)
                os.unlink(file)

    @staticmethod
    def set_timer(update: Update, context: CallbackContext) -> None:
        """Start the CCTV job. This job pushes photos when motion is detected in the camera frame."""
        _CCTV_PROCESS = subprocess.Popen(sys.executable, os.getcwd() + "motion_detection.py")
        
        chat_id = update.message.chat_id

        due = int(UPDATE_RATE)

        job_removed = Cctv.remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(Cctv.alarm, due, context=chat_id, name=str(chat_id))

        text = 'Job successfully started!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    @staticmethod
    def unset(update: Update, context: CallbackContext) -> None:
        """Stop the CCTV job."""

        chat_id = update.message.chat_id
        job_removed = Cctv.remove_job_if_exists(str(chat_id), context)

        if not job_removed:
            _CCTV_PROCESS.terminate()
            sleep(1)
            if _CCTV_PROCESS.returncode() is None:
                _CCTV_PROCESS.kill()

        text = 'Job successfully cancelled!' if job_removed else 'You have no active job.'
        update.message.reply_text(text)