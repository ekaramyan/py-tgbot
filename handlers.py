import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, MessageHandler, Filters
from utils import build_menu
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
FILES_DIR = os.path.join(os.getcwd(), 'files')


def start(update: Update, context: CallbackContext) -> None:
    some_strings = ["Отправить фото подтверждения покупки",
                    "Отправить видео подтверждения получения",
                    "Статус проверки кэшбека"]
    button_list = [s for s in some_strings]
    reply_markup = ReplyKeyboardMarkup(build_menu(
        button_list, n_cols=1), resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Добро пожаловать! Для получения кэшбека откройте меню и отправьте для начала подтверждение своей покупки.", reply_markup=reply_markup)


def receive_cashback(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Отправить фото подтверждения покупки":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Отправьте фото подтверждения покупки")
        context.dispatcher.add_handler(
            MessageHandler(Filters.photo, receive_photo))
        context.job_queue.run_once(cancel_request_data, 60, context=[
                                   update.message.chat_id, update.message.message_id])
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Для получения кэшбека откройте меню и отправьте для начала подтверждение своей покупки.")


def receive_photo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за фото! Отправьте видео подтверждения получения, чтобы мы могли начать обработку.")
    context.dispatcher.add_handler(
        MessageHandler(Filters.video, receive_video))
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


def receive_video(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за видео! Ожидайте проверки аналитиком данных, вы так же можете отследить стстус получения кэшбека в соответствующем пункте меню.")
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == "confirm_purchase":
        context.bot.send_message(
            chat_id=query.message.chat_id, text="Отправьте фото подтверждения покупки")
        context.dispatcher.add_handler(
            MessageHandler(Filters.photo, receive_photo))
        context.job_queue.run_once(cancel_request_data, 60, context=[
                                   query.message.chat_id, query.message.message_id])
    elif query.data == "confirm_receipt":
        context.bot.send_message(
            chat_id=query.message.chat_id, text="Отправьте видео подтверждения получения")
        context.dispatcher.add_handler(
            MessageHandler(Filters.video, receive_video))
        context.job_queue.run_once(cancel_request_data, 60, context=[
                                   query.message.chat_id, query.message.message_id])
    elif query.data == "check_cashback_status":
        status_message = "Статус проверки кэшбека: В обработке"
        context.bot.send_message(
            chat_id=query.message.chat_id, text=status_message)
