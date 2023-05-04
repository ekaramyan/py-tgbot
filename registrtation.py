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

# Определяем константы для состояний
NAME, PHONE_NUMBER, CARD_NUMBER, FINISH = range(4)


CARD_NUMBER_REGEX = re.compile(r'^\d{16}$')


def validate_card_number(card_number: str) -> bool:
    return bool(CARD_NUMBER_REGEX.match(card_number))


def start_registration(update: Update, context: CallbackContext) -> int:
    # Переходим в состояние NAME и запрашиваем ФИО
    update.message.reply_text(
        'Для регистрации введите свои ФИО:',
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


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

    username = update.message.from_user.username
    context.user_data['username'] = username
    # Переходим в состояние FINISH и показываем пользователю результаты регистрации
    update.message.reply_text(
        f'@{username}, Вы успешно зарегистрированы в системе.',
        reply_markup=ReplyKeyboardRemove()
    )
    return FINISH


def cancel_registration(update: Update, context: CallbackContext) -> int:
    # Очищаем user_data и завершаем регистрацию
    context.user_data.clear()
    update.message.reply_text(
        'Регистрация отменена. Для начала регистрации снова введите команду /start.'
    )
    return ConversationHandler.END


#     # Создаем ConversationHandler и задаем его состояния
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start_registration)],
#         states={
#             NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
#             PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_phone_number)],
#             CARD_NUMBER: [MessageHandler(Filters.text & ~Filters.command, get_card_number)],
#             FINISH: [MessageHandler(
#                 Filters.text & ~Filters.command, cancel_registration)]
#         },
#         fallbacks=[CommandHandler('cancel', cancel_registration)]
#     )

#     # Регистрируем ConversationHandler в updater'е


# if __name__ == '__main__':
#     main()
