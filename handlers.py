import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler, Updater
from utils import build_menu
from registrtation import NAME, PHONE_NUMBER, CARD_NUMBER, FINISH, start_registration, get_name, get_phone_number, get_card_number, cancel_registration
import os

# Словарь, в котором будут храниться пользователи и их данные
users = {}
SOME_STRINGS = ["Отправить фото подтверждения покупки",
                "Отправить видео подтверждения получения",
                "Кэшбеки"]
BACK_KEYBOARD = ['Назад']
CASHBACK_KEYBOARD = ['Ваши кэшбеки',
                     'Доступные кэшбеки',
                     'Архивные кэшбеки',
                     'Назад']

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



без регистрации кнопки отправки и кэшбеков должны быть не кликабельными (наверное)

Почему удаляеться отправленное фото?

Кнопка регистрации отдельно

"""


def main_menu(chat_id: int, context: CallbackContext, text: str = "Выберите нужный пункт меню", reply_markup=None) -> None:
    reply_markup = ReplyKeyboardMarkup(build_menu(
        SOME_STRINGS, n_cols=1), resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text=text,
                             reply_markup=reply_markup)


def start(update: Update, context: CallbackContext) -> None:
    if update.callback_query:
        main_menu(update.effective_chat.id, context)
        context.user_data["previous_menu"] = "start_menu"
        if update.callback_query.data == "Кэшбеки":
            cashback_menu(update, context)
            context.user_data["previous_menu"] = "cashback_menu"
    else:
        main_menu(update.effective_chat.id, context,
                  text="Добро пожаловать! Для получения кэшбека для начала зарегистрируйтесь, а после откройте меню и отправьте подтверждение своей покупки.")
        user = update.effective_user
        if user.id not in users:
            users[user.id] = {"name": user.first_name, "phone": None}
            context.bot.send_message(
                chat_id=user.id, text="Перед началом работы необходимо зарегестрироваться командой /registration")
        else:
            context.bot.send_message(chat_id=user.id, text="С возвращением!")


def register_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('registration', start_registration)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_phone_number)],
            CARD_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_card_number)],
            FINISH: [MessageHandler(
                Filters.text & ~Filters.command, cancel_registration)]
        },
        fallbacks=[CommandHandler('cancel', cancel_registration)])


def cashback_menu(update: Update, context: CallbackContext, reply_markup=None) -> None:
    reply_markup = reply_markup or ReplyKeyboardMarkup(build_menu(
        CASHBACK_KEYBOARD, n_cols=2), resize_keyboard=True)
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text='Выберите нужный пункт меню',
        reply_markup=reply_markup)
    # Сохраняем reply_markup в user_data
    context.user_data["reply_markup"] = reply_markup
    # Сохраняем предыдущее меню в user_data
    context.user_data["previous_menu"] = "main_menu"


def receive_photo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за фото! Отправьте видео подтверждения получения, чтобы мы могли начать обработку.")
    context.dispatcher.add_handler(
        MessageHandler(Filters.video, receive_video))
    """
    оно где-то сохраняется или отправляется?

    """
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


def receive_video(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Спасибо за видео! Ожидайте проверки аналитиком данных, вы так же можете отследить статус получения кэшбека в соответствующем пункте меню.")
    context.job_queue.run_once(cancel_request_data, 60, context=[
                               update.message.chat_id, update.message.message_id])


def back_to_menu(update: Update, context: CallbackContext, reply_markup=None) -> None:
    previous_menu = context.user_data.get("previous_menu")
    if previous_menu == "cashback_menu":
        main_menu(update.effective_chat.id, context, text="Выберите нужный пункт меню",
                  reply_markup=context.user_data.get("reply_markup"))
        context.user_data["previous_menu"] = "main_menu"
    else:
        main_menu(update.effective_chat.id, context,
                  text="Выберите нужный пункт меню")


def receive_cashback(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Отправить фото подтверждения покупки":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Отправьте фото подтверждения покупки")
        context.dispatcher.add_handler(
            MessageHandler(Filters.photo, receive_photo))

        context.job_queue.run_once(cancel_request_data, 60, context=[
            update.message.chat_id, update.message.message_id])

    elif update.message.text == "Отправить видео подтверждения получения":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Отправьте видео подтверждения получения товара, желательно, где ввы отрезаете этикетку, чтобы мы были уверене, что не будет возврата товара")
        context.dispatcher.add_handler(
            MessageHandler(Filters.photo, receive_photo))

        context.job_queue.run_once(cancel_request_data, 60, context=[
            update.message.chat_id, update.message.message_id])
    elif update.message.text == "Кэшбеки":

        reply_markup = ReplyKeyboardMarkup(build_menu(
            CASHBACK_KEYBOARD, n_cols=2), resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Для получения кэшбека выберите доступный кэшбек и начните процесс подтверждения покупки и получения заказа.", reply_markup=reply_markup)
        context.user_data["previous_menu"] = "cashback_menu"

    elif update.message.text == "Назад":
        back_to_menu(update, context,
                     reply_markup=context.user_data.get("reply_markup"))
        # Если пользователь был в меню "Кэшбеки", то второй раз нажатие на кнопку "Назад" возвращает его на предыдущее меню
        if context.user_data.get("previous_menu") == "cashback_menu":
            back_to_menu(update, context,
                         reply_markup=context.user_data.get("reply_markup"))


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
