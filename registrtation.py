from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)
from phonenumbers import parse, PhoneNumberFormat
import re
import utils
from menu import main_menu, check_registration

# Определяем константы для состояний
NAME, PHONE_NUMBER, CARD_NUMBER, TG_NICK, FINISH = range(5)


CARD_NUMBER_REGEX = re.compile(r'^\d{16}$')


def is_valid_name(name: str) -> bool:
    # Проверяем, состоит ли имя из трех слов, разделенных пробелами
    pattern = r'^[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+$'
    return bool(re.match(pattern, name))


def validate_card_number(card_number: str) -> bool:
    return bool(CARD_NUMBER_REGEX.match(card_number))


def start_registration(update: Update, context: CallbackContext) -> int:
    is_registered = check_registration(update, context)
    tg_user = update.message.from_user
    if is_registered:
        context.user_data["is_registered"] = True
        return context.bot.send_message(
            chat_id=tg_user.id, text=f"{tg_user.first_name}, вы уже зарегестрированы")
    else:
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
   
    name = update.message.text.strip()
    if not is_valid_name(name):
        update.message.reply_text('Некорректное ФИО. Введите ФИО, состоящее из имени, фамилии и отчества, разделенных пробелами.')
        return NAME
    context.user_data['name'] = update.message.text

    update.message.reply_text(
        'Введите свой номер телефона в международном формате (например, +12345678910), нужен номер на который привязан ваш СБП, чтобы мы смогли вам выплачивать кэшбек:'
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
    # Переходим в состояние CARD_NUMBER и запрашиваем номер банковской карты или предлагаем пропустить
    reply_keyboard = [['Пропустить']]
    update.message.reply_text(
        'Введите номер вашей банковской карты в формате 16 цифр без пробелов XXXXXXXXXXXXXXXX '
        'или нажмите кнопку "Пропустить", если не хотите вносить эти данные:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CARD_NUMBER


def get_card_number(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'пропустить':
        context.user_data['card_number'] = None
    else:
        # Сохраняем введенный номер банковской карты в user_data
        card_number = update.message.text
        if not validate_card_number(card_number):
            update.message.reply_text(
                'Номер банковской карты некорректный. Попробуйте снова:'
            )
            return CARD_NUMBER
        context.user_data['card_number'] = card_number

    tg_user = update.message.from_user    

    utils.register_user(
        firstName=context.user_data['name'].split()[1],
        lastName=context.user_data['name'].split()[0],
        middleName=context.user_data['name'].split()[-1],
        phoneNumber=context.user_data['phone_number'],
        creditCartNumber=context.user_data['card_number'],
        tgNickname=tg_user.username,
        tg_id=tg_user.id,
        bannedText=''
    )
    # Переходим в состояние FINISH и показываем пользователю результаты регистрации
    update.message.reply_text(
        f'@{tg_user.username}, Вы успешно зарегистрированы, можете начать участие в акциях кэшбека.',
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
