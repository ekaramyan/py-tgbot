from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, add_to_my_cashbacks, build_menu, cashbacks_users_history, get_tg_nickname
from cashback_buttons import get_pagination, available_cashbacks_handler



def delete_message(update: Update, context: CallbackContext):
    query = update.callback_query
    query.message.delete()

def cashback_details_handler(update: Update, context: CallbackContext):
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

    if query.data.startswith("cashback_details_"):
        item_id = query.data.replace("cashback_details_", "")
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
                text += f"ссылка на вб: {cashback['linkOnSite']}\n"
                text += f"артикль: {cashback['article']}\n"

                buttons = [
                        InlineKeyboardButton("Участвовать", callback_data=f"cashback_details_{item_id}_participate"),
                        InlineKeyboardButton("Назад", callback_data=f"cashback_details_{item_id}_not_participate")
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
        user_nick = update.effective_user.username
        user_id = get_tg_nickname(user_nick).json()["data"]["id"]
        print(cashback_id)
        cashbackActionId = cashback_id
        cashbackItemId = cashback_id
        cashbackUserId = user_id
        cashbackContractStatusId = 0
        response = add_to_my_cashbacks(cashbackActionId, cashbackItemId, cashbackUserId, cashbackContractStatusId)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Поздравляем! Вы участвуете в кэшбеке.")
        
        # на {cashback['name']}