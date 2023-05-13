from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from utils import build_menu, get_tg_nickname


def check_registration(update: Update, context: CallbackContext) -> bool:
    chat_id = update.message.chat_id
    user = update.effective_user
    tg_nickname = user.username
    # tg_nickname = user.username if user else None
    response = get_tg_nickname(tg_nickname).json()["data"]
    if response:
        print("true")
        context.user_data['is_registered'] = True
        return True
    else:
        context.bot.send_message(
            chat_id=chat_id, text="Для использования функций бота необходимо зарегистрироваться. Вы не сможете пользоапться ботом, пока вы не зарегестрироавлись. /registration")
        context.user_data['is_registered'] = False
        return False



SOME_STRINGS = ["Аккаунт",
                "Кэшбеки"]

ACCOUNT_KEYBOARD = ["Изменить информацию",
                    "Удалить аккаунт"]

BACK_KEYBOARD = ['Назад']
CASHBACK_KEYBOARD = ['Ваши кэшбеки',
                     'Доступные кэшбеки',
                     'Архивные кэшбеки',
                     'Назад']


def main_menu(chat_id: int, context: CallbackContext, text: str = "Выберите нужный пункт меню", reply_markup=None) -> None:
    if not context.user_data.get("is_registered", False):
        # context.bot.send_message(
        #     chat_id=chat_id, text="Добро пожаловать! Вы не зарегестрированы, зарегестрируйтесь")
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

    if reply_markup:
        buttons = reply_markup.keyboard
        for row in buttons:
            for button in row:
                if button.text == 'Доступные кэшбеки':
                    button.callback_data = 'available_cashbacks'


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
    #cскопировать в aprove
    if  update.message.text == "Аккаунт":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text="Еще в разработке")
        
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
