import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler
from menu import main_menu, cashback_menu, check_registration
from registrtation import NAME, PHONE_NUMBER, CARD_NUMBER, FINISH, start_registration, get_name, get_phone_number, get_card_number, cancel_registration, finish_registration
from utils import request_files, get_tg_nickname
import os
import math
import random
# ff

# Словарь, в котором будут храниться пользователи и их данные
users = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
FILES_DIR = os.path.join(os.getcwd(), 'files')


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    is_registered = check_registration(update, context)
    if is_registered:
        context.bot.send_message(
            chat_id=user.id, text=f"С возвращением, {user.first_name}!")
        main_menu(update.effective_chat.id, context)
        context.user_data["previous_menu"] = "start_menu"
    else:
        main_menu(update.effective_chat.id, context,
                  text="Добро пожаловать! Для получения кэшбека для начала зарегистрируйтесь, а после откройте меню и отправьте подтверждение своей покупки.")
        if user.id not in users:
            users[user.id] = {"name": user.first_name, "phone": None}
            # context.bot.send_message(
            #     chat_id=user.id, text="Перед началом работы необходимо зарегистрироваться командой, до регистрации все функции бота заблокированы /registration")



def register_handler() -> ConversationHandler:

    return ConversationHandler(
        entry_points=[CommandHandler('registration', start_registration)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_phone_number)],
            CARD_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_card_number)],
            FINISH: [MessageHandler(
                    Filters.text & ~Filters.command, finish_registration)]
        },
        fallbacks=[CommandHandler('cancel', cancel_registration)])


def receive_video(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за видео! Ожидайте проверки аналитиком данных, вы также можете отследить статус получения кэшбека в соответствующем пункте меню.")
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])

    # Отправка видео на сервер
    id = 123  # Замените на соответствующий идентификатор
    condition = 2  # Замените на соответствующее условие
    path_to_video = "path/to/video.mp4"  # Замените на путь к файлу видео
    response = request_files(id, condition, path_to_video)
    if response.status_code == 200:
        print("Видео успешно отправлено на сервер")
    else:
        print("Произошла ошибка при отправке видео на сервер")


def receive_photo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за фото! Отправьте видео подтверждения получения, чтобы мы могли начать обработку.")
    context.dispatcher.add_handler(
        MessageHandler(Filters.video, receive_video))

    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


    user_id = update.effective_user.id
    photo_file = update.message.photo[-1].get_file()
    path_to_photo = f"files/photo_{user_id+random}.jpg"
    photo_file.download(path_to_photo)
    id = int(math.ceil(user_id*random))
    condition = 1
    response = request_files(id, condition, path_to_photo)
    if response.status_code == 200:
        print("Фото успешно отправлено на сервер")
    else:
        print("Произошла ошибка при отправке фото на сервер")


def cancel_request_data(context: CallbackContext) -> None:
    chat_id, message_id = context.job.context
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)


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
