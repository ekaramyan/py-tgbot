from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import my_cashbacks, request_files, build_menu, get_tg_id
import datetime
import os


def handle_file(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_file'):
        if update.message and (update.message.document or update.message.photo or update.message.video or update.message.voice):
            file = update.message.document or update.message.photo or update.message.video or update.message.voice
            file_obj = file[-1].get_file()  # Получаем объект файла из сообщения
            context.user_data['awaiting_file'] = False
            cashback_id = context.user_data.get('cashback_id')
            condition = context.user_data.get('condition')
            file_bytes = file_obj.download_as_bytearray()  # Получаем содержимое файла в виде bytes
            process_data(update, context, cashback_id, condition, file_bytes)
        else:
            # Обработка случая, когда сообщение не содержит документа
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Пожалуйста, отправьте файл (документ, фото, видео или голосовое сообщение).")



def process_data(update: Update, context: CallbackContext, cashback_id, condition, file) -> None:
    try:
        response = request_files(cashback_id, condition, file)

        if response.status_code == 200:
            print("Файл успешно отправлен на сервер")
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Поздравляем! Вы успешно отправили файл на {condition} этап")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ошибка при отправке файла на сервер. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        # Обработка ошибки при отправке файла
        print(f"Ошибка при отправке файла: {str(e)}")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Произошла ошибка при отправке файла. Пожалуйста, попробуйте еще раз.")


def generate_cashback_message(cashback, conditions, item_id):
    true_conditions = conditions

    text = "Полные данные о кэшбеке:\n"
    photo = cashback['cashbackAction']['photo']
    text += f"Дней на выполнение условий: {cashback['cashbackAction']['daysAction']}\n"
    text += f"Название: {cashback['cashbackAction']['name']}\n"
    text += f"Выполнено: {true_conditions}/{5}\n"
    text += f"Доступных размеров: {cashback['cashbackItem']['count']}/{cashback['cashbackItem']['remains']}\n"
    text += f"Этапы: {cashback['cashbackAction']['actionText']}\n\n"
    text += f"Процент кэшбека: {cashback['cashbackAction']['cashbackPercentage']}\n"

    buttons = [
        InlineKeyboardButton("Выполнить новый этап", callback_data=f"cashback_aproval_{item_id}_aproved"),
        InlineKeyboardButton("Назад", callback_data=f"cashback_aproval_{item_id}_canceled")
    ]
    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2))

    return photo, text, keyboard




def cashback_aprove_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    # print(f"query.data: {query.data}")
    limit = 25
    current_page = 0
    tg_id = update.effective_user.id
    user_id = get_tg_id(tg_id).json()["data"]["id"]
    response = my_cashbacks(user_id=user_id, limit=limit, page=current_page)
    cashbacks_data = response["data"]

    true_conditions = 0

    cashback = None

    if query.data.startswith("cashback_aproval_" or "cashback_history_"):

        item_id = query.data.replace("cashback_aproval_", "")
        # print(f"item_id: {item_id}")
        items = cashbacks_data["data"]
        cashback_id = int(item_id.split('_')[0])

        try:

            item_id = int(cashback_id)

            for item in items:
                compare_id = int(item["id"])
                if compare_id == item_id:
                    cashback = item
                    break
                else:
                    continue

            if cashback is not None and item_id is not None:


                for key, value in cashback["cashbackContractStatus"].items():
                    if key.startswith("isCondition") and value == True:
                        true_conditions += 1

                if(not query.data.endswith("_canceled") and not query.data.endswith("_aproved")):
                    photo, text, keyboard = generate_cashback_message(cashback, true_conditions, item_id)
                    query.message.reply_photo(photo, caption=text, reply_markup=keyboard)

            else:
                print("Invalid cashback_id")
        except ValueError:
            print("Invalid item_id")        
    else:
        print("Invalid query data format")

    print(query.data)
    if query.data.endswith("_canceled"):
        print("no")
        query.message.delete()
        print(query.data)

    elif query.data.endswith("_aproved"):
        print("yes")

        condition = 0

        if(true_conditions<5):
            condition = true_conditions+1


        context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Отправьте данные для прохождения {condition} этапа (фото, документ, голосовое сообщение или видео).")
        

        context.user_data['awaiting_file'] = True
        context.user_data['cashback_id'] = cashback_id
        context.user_data['condition'] = condition

        # request_data(update, context, cashback_id, condition)