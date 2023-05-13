from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, request_files, build_menu, get_tg_nickname
# from cashback_buttons import get_user_cashbacks, available_cashbacks_handler
import math
import random



def delete_message(update: Update):
    query = update.callback_query
    query.message.delete()

def process_data(update: Update, context: CallbackContext, user_id, condition) -> None:
    if context.user_data.get('awaiting_file'):
        file = None
        file_type = None

        if update.effective_message.photo:
            file = update.effective_message.photo[-1].get_file()
            file_type = "фото"
        elif update.effective_message.document:
            file = update.effective_message.document.get_file()
            file_type = "документ"
        elif update.effective_message.voice:
            file = update.effective_message.voice.get_file()
            file_type = "голосовое сообщение"
        elif update.effective_message.video:
            file = update.effective_message.video.get_file()
            file_type = "видео"

        if file:
            path_to_file = f"files/{file_type}_{user_id+random}"
            path_to_file += ".jpg" if file_type == "фото" else ""
            path_to_file += ".pdf" if file_type == "документ" else ""
            path_to_file += ".ogg" if file_type == "голосовое сообщение" else ""
            path_to_file += ".mp4" if file_type == "видео" else ""
            file.download(path_to_file)
            id = int(math.ceil(user_id*random))

            response = request_files(id, condition, path_to_file)

            if response.status_code == 200:
                print("Файл успешно отправлен на сервер")
                context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=f"Поздравляем! Вы успешно отправили {file_type} на {condition} этап")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                    text="Неверный тип файла, пожалуйста, отправьте фото, документ, голосовое сообщение или видео.")
            # Сброс состояния ожидания файла
        context.user_data['awaiting_file'] = False
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ошибка на сервере, файл не отправлен.")
        print("Произошла ошибка при отправке файла на сервер")

        


def cashback_aprove_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    # print(f"query.data: {query.data}")

    limit = 25
    current_page = 0
    response = get_cashbacks(status_id=0, limit=limit, page=current_page)
    cashbacks_data = response.json()["data"]

    cashback = None
    # {"name":None, "linkOnSite":None}

    item_id=None
    cashback_id = None

    if query.data.startswith("cashback_aproval_"):
        item_id = query.data.replace("cashback_aproval_", "")
        # print(f"item_id: {item_id}")
        items = cashbacks_data["data"]
        cashback_id = int(item_id.split('_')[0])

        try:
            item_id = int(item_id)


            for item in items:
                compare_id = int(item["id"])
                if compare_id == item_id:
                    cashback = item["product"]
                    break
                else:
                    continue

            if cashback is not None:
                text = "Полные данные о кэшбеке:\n"
                # photo = cashback['defaultImageUrl']
                text += f"Название: {cashback['name']}\n"
                text += f"Этапы: {cashback['linkOnSite']}\n"
                text += f"Текущий статус: {cashback['article']}\n"

                buttons = [
                        InlineKeyboardButton("Выполнить новый этап", callback_data=f"cashback_aproval_{item_id}_aproved"),
                        InlineKeyboardButton("Назад", callback_data=f"cashback_aproval_{item_id}_canceled")
                    ]
                keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2))


                query.message.reply_text(text, reply_markup=keyboard)
            else:
                print("Invalid item_id")
        except ValueError:
            print("Invalid item_id")        
    else:
        print("Invalid query data format")


    if query.data.endswith("_canceled"):
        print("no")
        delete_message(update)

    elif query.data.endswith("_aproved"):
        print("yes")
        user_nick = update.effective_user.username
        user_id = get_tg_nickname(user_nick).json()["data"]["id"]
        condition = 1

        context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Отправьте данные для прохождения {condition} этапа (фото, документ, голосовое сообщение или видео).")
        

        context.user_data['awaiting_file'] = True

        process_data(update, context, user_id, condition)
        
        print(cashback_id)






    # if update.message.text == "Отправить фото подтверждения покупки":
    #     context.bot.send_message(chat_id=update.effective_chat.id,
    #                              text="Отправьте фото подтверждения покупки")
    #     context.dispatcher.add_handler(
    #         MessageHandler(Filters.photo, receive_photo))

    #     context.job_queue.run_once(cancel_request_data, 60, context=[
    #         update.message.chat_id, update.message.message_id])

    # elif update.message.text == "Отправить видео подтверждения получения":
    #     context.bot.send_message(chat_id=update.effective_chat.id,
    #                              text="Отправьте видео подтверждения получения товара, желательно, где ввы отрезаете этикетку, чтобы мы были уверене, что не будет возврата товара")
    #     context.dispatcher.add_handler(
    #         MessageHandler(Filters.photo, receive_photo))

    #     context.job_queue.run_once(cancel_request_data, 60, context=[
    #         update.message.chat_id, update.message.message_id])