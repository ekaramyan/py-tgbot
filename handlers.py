from telegram import ReplyKeyboardMarkup, KeyboardButton
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,  KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler
from utils import build_menu
import os
import requests

# Словарь, в котором будут храниться пользователи и их данные
users = {}
BACK_KEYBOARD = ReplyKeyboardMarkup([['Назад']])

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
FILES_DIR = os.path.join(os.getcwd(), 'files')

"""
Зачем  button_list = ["Назад"] + some_strings при старте?

        if user.id not in users:

            users[user.id] = {"name": user.first_name, "phone": None}
            context.bot.send_message(
                chat_id=user.id, text="Напиши мне свой номер телефона")
        else:
            context.bot.send_message(chat_id=user.id, text="С возвращением!")

нужно зарегать а не просто вопрос

json_data = {
    'password': 'string',
    'roleId': 0,
    'photo': 'string',
    'firstName': 'string',
    'lastName': 'string',
    'email': 'user@example.com',
    'login': 'string',
    'phone': 'string',
    'tg': 'string',

данные для сбора



без регистрации кнопки отпраки и кэшбеков должны быть не кликабельными (наверное)

Почему удаляеться отправленное фото?

Кнопка регистрации отдельно

"""
def start(update: Update, context: CallbackContext) -> None:
    some_strings = ["Отправить фото подтверждения покупки",
                    "Отправить видео подтверждения получения",
                    "Кэшбеки"]
    
    if update.callback_query:

        # button_list = ["Назад"] + some_strings

        reply_markup = ReplyKeyboardMarkup(build_menu(
            some_strings, n_cols=1), resize_keyboard=True)
        
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                 text="Выберите нужный пункт меню", reply_markup=reply_markup)
        
        context.user_data["previous_menu"] = "start_menu"

    else:
        # button_list = some_strings + ["Назад"]

        reply_markup = ReplyKeyboardMarkup(build_menu(
            some_strings, n_cols=1), resize_keyboard=True)
        
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Добро пожаловать! Для получения кэшбека для начала зарегистрируйтесь, а после откройте меню и отправьте подтверждение своей покупки.", reply_markup=reply_markup)
        
        
        user = update.effective_user

        if user.id not in users:

            users[user.id] = {"name": user.first_name, "phone": None}
            context.bot.send_message(
                chat_id=user.id, text="Напиши мне свой номер телефона")
        else:
            context.bot.send_message(chat_id=user.id, text="С возвращением!")



"""
где используеться?
нужно не только номер
"""
def register_phone(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in users:
        context.bot.send_message(
            chat_id=user_id, text="Сначала напиши /start, чтобы зарегистрироваться.")
    else:
        try:
            phone = int(update.message.text)
            users[user_id]["phone"] = phone
            context.bot.send_message(
                chat_id=user_id, text="Спасибо! Теперь можем приступить к получению кэшбека, твой номер телефона: {}.".format(phone))
        except ValueError:
            context.bot.send_message(
                chat_id=user_id, text="Напиши свой номер телефона цифрами, пожалуйста.")


def cashback_menu(update, context):
    chat_id = update.message.chat_id

    # Создаем кнопки для меню
    button1 = InlineKeyboardButton(
        'Ваши кэшбеки', callback_data='your_cashback')
    button2 = InlineKeyboardButton(
        'Доступные кэшбеки', callback_data='available_cashback')
    button3 = InlineKeyboardButton(
        'Архивные кэшбеки', callback_data='archived_cashback')

    # Создаем меню
    reply_markup = InlineKeyboardMarkup([[button1], [button2], [button3]])
    """
    должно вернуть на первоначальное меню, а не выводить сообщением кнопки
    """
    # Отправляем сообщение с меню
    context.bot.send_message(
        chat_id=chat_id, text='Выберите нужный пункт меню', reply_markup=reply_markup)

    # Сохраняем предыдущее меню в user_data
    context.user_data["previous_menu"] = "cashback_menu"


def receive_photo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за фото! Отправьте видео подтверждения получения, чтобы мы могли начать обработку.")
    context.dispatcher.add_handler(
        MessageHandler(Filters.video, receive_video)) 
    """
    оно где-то сохраняеться или отправляеться?

    """
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


def receive_video(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за видео! Ожидайте проверки аналитиком данных, вы так же можете отследить статус получения кэшбека в соответствующем пункте меню.")
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])



def back_to_menu(update: Update, context: CallbackContext) -> None:

    previous_menu = context.user_data.get("previous_menu")
    if previous_menu == "cashback_menu":
        cashback_menu(update, context)
    else:
        some_strings = ["Отправить фото подтверждения покупки",
                        "Отправить видео подтверждения получения",
                        "Кэшбеки"]
        
        button_list = ["Назад"] + some_strings

        reply_markup = ReplyKeyboardMarkup(build_menu(
            button_list, n_cols=1), resize_keyboard=True)
        
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Выберите нужный пункт меню", reply_markup=reply_markup)
        
        context.user_data["previous_menu"] = "back_to_menu"

    # Удаляем текущее меню
    context.bot.delete_message(chat_id=update.effective_chat.id,
                               message_id=update.effective_message.message_id)

    # Отправляем предыдущее меню
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Выберите действие:',
                             reply_markup=some_strings + ['Назад'])
    """
    зачем   reply_markup=some_strings + ['Назад']) ? 
    """
    context.user_data["previous_menu"] = "main_menu"


def receive_cashback(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Отправить фото подтверждения покупки":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Отправьте фото подтверждения покупки")
        context.dispatcher.add_handler(
            MessageHandler(Filters.photo, receive_photo))
        
        context.job_queue.run_once(cancel_request_data, 60, context=[
            update.message.chat_id, update.message.message_id])
        
    elif update.message.text == "Кэшбеки":
        some_strings = ['Ваши кэшбеки',
                        'Доступные кэшбеки',
                        'Архивные кэшбеки',
                        'Назад']
        

        # button_list = [s for s in some_strings]

        """
        some_strings сделать глобальной
        button_list = [s for s in some_strings] зачем это?
        """
        reply_markup = ReplyKeyboardMarkup(build_menu(
            some_strings, n_cols=1), resize_keyboard=True)
        
        
        
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Для получения кэшбека выберите доступный кэшбек и начните процесс подтверждения покупки и получения заказа.", reply_markup=reply_markup)
        context.user_data["previous_menu"] = "cashback_menu"


    elif update.message.text == "Назад":
        back_to_menu(update, context)


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
