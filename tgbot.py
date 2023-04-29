import logging
from telegram import Update, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram.utils.request import Request
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# путь для сохранения файлов
FILES_DIR = os.path.join(os.getcwd(), 'files')

TOKEN = '6134723312:AAFy2KiaQZQQdtDQL66OrZRs8QmBSAm1wxk'


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons] if not isinstance(
            header_buttons, list) else header_buttons)
    if footer_buttons:
        menu.append([footer_buttons] if not isinstance(
            footer_buttons, list) else footer_buttons)
    return menu


def start(update: Update, context: CallbackContext) -> None:
    some_strings = ["Отправить фото подтверждения покупки",
                    "Отправить видео подтверждения получения", "Статус проверки кэшбека"]
    button_list = [s for s in some_strings]
    reply_markup = ReplyKeyboardMarkup(build_menu(
        button_list, n_cols=1), resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Добро пожаловать! Для получения кэшбека отправьте фото/видео подтверждения покупки.", reply_markup=reply_markup)


def receive_cashback(update: Update, context):
    # Получаем файл из сообщения пользователя
    try:
        if update.message.photo:
            file = context.bot.get_file(update.message.photo[-1].file_id)

            # Создаем директорию, если ее нет
            if not os.path.exists(FILES_DIR):
                os.makedirs(FILES_DIR)

            # Сохраняем файл на диск
            file_name = os.path.join(FILES_DIR, file.file_path.split('/')[-1])
            file.download(file_name)

            # Отправляем сообщение о выдаче кэшбека
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Кэшбек выдан.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Пожалуйста, отправьте фото для получения кэшбека.")
    except AttributeError:
        logging.error('UnionType error occurred')


def button_callback(update, context):
    query = update.callback_query
    query.answer()
    text = query.data
    if text == "Отправить фото подтверждения покупки":
        request_data(update, context)
    elif text == "Отправить видео подтверждения получения":
        pass
    elif text == "Статус проверки кэшбека":
        pass


async def request_data(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Пожалуйста, отправьте фото для проверки.")

    def callback(update, context):
        if update.message.photo:
            receive_cashback(update, context)
            context.dispatcher.remove_handler(photo_handler)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Пожалуйста, отправьте фото для проверки.")

    photo_handler = MessageHandler(Filters.photo, callback)
    context.dispatcher.add_handler(photo_handler)

    context.job_queue.run_once(
        cancel_request_data, 60, context=update.effective_chat.id)


def cancel_request_data(context):
    chat_id = context.job.context
    context.bot.send_message(chat_id=chat_id, text="Время ожидания истекло.")
    context.dispatcher.remove_handler(photo_handler)

 # добавляем обработчик для кнопки "Запросить фото..."
    request_data_handler = CommandHandler('request_data', request_data)
    context.dispatcher.add_handler(request_data_handler)


# создаем обработчики для команд
updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(
    Filters.photo | Filters.video, receive_cashback))

request_data_handler = CommandHandler('request_data', request_data)
updater.dispatcher.add_handler(request_data_handler)

updater.start_polling()
updater.idle()

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    text = query.data
    if text == "Отправить фото подтверждения покупки":
        request_data(update, context)
    elif text == "Отправить видео подтверждения получения":
        pass
    elif text == "Статус проверки кэшбека":
        # выполнение функции для кнопки "Статус проверки кэшбека"
        pass

