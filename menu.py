from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters
from utils import build_menu

def check_registration(update: Update, context: CallbackContext) -> bool:
    chat_id = update.message.chat_id
    if not context.user_data.get("is_registered", False):
        context.bot.send_message(chat_id=chat_id, text="Для использования функций бота необходимо зарегистрироваться. /registration")
        return False
    return True

SOME_STRINGS = ["Отправить фото подтверждения покупки",
                "Отправить видео подтверждения получения",
                "Кэшбеки"]
BACK_KEYBOARD = ['Назад']
CASHBACK_KEYBOARD = ['Ваши кэшбеки',
                     'Доступные кэшбеки',
                     'Архивные кэшбеки',
                     'Назад']


def main_menu(chat_id: int, context: CallbackContext, text: str = "Выберите нужный пункт меню", reply_markup=None) -> None:
    if not context.user_data.get("is_registered", False):
        context.bot.send_message(
            chat_id=chat_id, text="Для использования функций бота необходимо зарегистрироваться. /registration")
        return
    reply_markup = ReplyKeyboardMarkup(build_menu(
        SOME_STRINGS, n_cols=1), resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text=text,
                             reply_markup=reply_markup)


def cashback_menu(update: Update, context: CallbackContext, reply_markup=None) -> None:
    if not check_registration(update, context):
        return  
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


def back_to_menu(update: Update, context: CallbackContext, reply_markup=None) -> None:
    if not check_registration(update, context):
        return
    previous_menu = context.user_data.get("previous_menu")
    if previous_menu == "cashback_menu":
        main_menu(update.effective_chat.id, context, text="Выберите нужный пункт меню",
                  reply_markup=context.user_data.get("reply_markup"))
        context.user_data["previous_menu"] = "main_menu"
    else:
        main_menu(update.effective_chat.id, context,
                  text="Выберите нужный пункт меню")


def receive_cashback(update: Update, context: CallbackContext) -> None:
    if not check_registration(update, context):
        return
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
