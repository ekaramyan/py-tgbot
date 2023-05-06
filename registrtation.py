from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from phonenumbers import parse, PhoneNumberFormat
import re
import utils
from menu import main_menu


# Определяем константы для состояний
NAME, PHONE_NUMBER, CARD_NUMBER, TG_NICK, FINISH = range(5)


CARD_NUMBER_REGEX = re.compile(r'^\d{16}$')


def validate_card_number(card_number: str) -> bool:
    return bool(CARD_NUMBER_REGEX.match(card_number))


def start_registration(update: Update, context: CallbackContext) -> int:
    # Переходим в состояние NAME и запрашиваем ФИО
    context.user_data["is_registered"] = False
    update.message.reply_text(
        'Для регистрации введите свои ФИО:',
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


def finish_registration(update: Update, context: CallbackContext) -> int:
    if not context.user_data.get("is_registered"):
        context.user_data["is_registered"] = True
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Регистрация завершена. Спасибо за регистрацию!'
        )
    else:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы уже зарегистрированы. Начните работу с ботом.'
        )
    return ConversationHandler.END


def get_name(update: Update, context: CallbackContext) -> int:
    # Сохраняем введенное ФИО в user_data
    context.user_data['name'] = update.message.text
    # Переходим в состояние PHONE_NUMBER и запрашиваем номер телефона
    update.message.reply_text(
        'Введите свой номер телефона в международном формате (например, +12345678910):'
    )
    return PHONE_NUMBER


def get_phone_number(update: Update, context: CallbackContext) -> int:
    # Проверяем, что введенный номер телефона является допустимым
    try:
        phone_number = parse(update.message.text, None)
        if not phone_number:
            raise ValueError()
    except ValueError:
        update.message.reply_text(
            'Вы ввели недопустимый номер телефона. Пожалуйста, попробуйте еще раз:'
        )
        return PHONE_NUMBER
    # Сохраняем введенный номер телефона в user_data
    context.user_data['phone_number'] = update.message.text
    # Переходим в состояние CARD_NUMBER и запрашиваем номер банковской карты
    update.message.reply_text(
        'Введите номер вашей банковской карт в формате 16 цифр без пробелов XXXXXXXXXXXXXXXX:'
    )
    return CARD_NUMBER


def get_card_number(update: Update, context: CallbackContext) -> int:
    # Сохраняем введенный номер банковской карты в user_data
    card_number = update.message.text
    if not validate_card_number(card_number):
        update.message.reply_text(
            'Номер банковской карты некорректный. Попробуйте снова:')
        return CARD_NUMBER
    context.user_data['card_number'] = card_number

    # Получаем никнейм пользователя
    username = update.message.from_user.username
    print(username)
    # передача даты на бэкенд
    utils.register_user(
        firstName=context.user_data['name'].split()[1],
        lastName=context.user_data['name'].split()[0],
        middleName=context.user_data['name'].split()[-1],
        phoneNumber=context.user_data['phone_number'],
        creditCartNumber=context.user_data['card_number'],
        tgNickname=username,
        bannedText=''
    )
    # Переходим в состояние FINISH и показываем пользователю результаты регистрации
    update.message.reply_text(
        f'@{username}, Вы успешно зарегистрированы, можете начать участие в акциях кэшбека.',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data["is_registered"] = True
    main_menu(update.effective_chat.id, context)
    return FINISH


def cancel_registration(update: Update, context: CallbackContext) -> int:
    if not context.user_data.get("is_registered"):
        context.user_data.clear()
        update.message.reply_text(
            'Регистрация отменена. Для начала регистрации снова введите команду /registration.'
        )
    return FINISH
