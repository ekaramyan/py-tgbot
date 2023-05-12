from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, add_to_my_cashbacks, build_menu, cashbacks_users_history
from cashback_buttons import get_pagination, available_cashbacks_handler

def delete_message(update: Update, context: CallbackContext):
    query = update.callback_query
    query.message.delete()

def cashback_details_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    # print(f"query.data: {query.data}")

    limit = 25  # количество элементов на странице
    current_page = 0
    response = get_cashbacks(status_id=0, limit=limit, page=current_page)
    cashbacks_data = response.json()["data"]

    cashback = {"name":"Нет Данных", "linkOnSite":"Нет Данных"}


    if query.data.startswith("cashback_details_"):
        item_id = query.data.replace("cashback_details_", "")
        # print(f"item_id: {item_id}")
        items = cashbacks_data["data"]

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
                text += f"Название: {cashback['name']}\n"
                text += f"Описание: {cashback['linkOnSite']}\n"

                buttons = [
                        InlineKeyboardButton("Участвовать", callback_data=f"cashback_details_{item_id}_participate"),
                        InlineKeyboardButton("Не участвовать", callback_data=f"cashback_details_{item_id}_not_participate")
                    ]
                keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2))


                query.message.reply_text(text, reply_markup=keyboard)
            else:
                print("Invalid item_id")
        except ValueError:
            print("Invalid item_id")        
    else:
        print("Invalid query data format")


    if query.data.endswith("_not_participate"):
        print("no")
        delete_message(update, context)
    elif query.data.endswith("_participate"):
        print("yes")
        #

    




