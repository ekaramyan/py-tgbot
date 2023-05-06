import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler
from menu import main_menu, cashback_menu
from registrtation import NAME, PHONE_NUMBER, CARD_NUMBER, FINISH, start_registration, get_name, get_phone_number, get_card_number, cancel_registration, finish_registration

import os


# Словарь, в котором будут храниться пользователи и их данные
users = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
FILES_DIR = os.path.join(os.getcwd(), 'files')


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
                Filters.text & ~Filters.command, finish_registration)]
        },
        fallbacks=[CommandHandler('cancel', cancel_registration)])


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
