from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, add_to_my_cashbacks, build_menu, get_tg_id
from cashback_buttons import get_pagination, available_cashbacks_handler



def delete_message(update: Update, context: CallbackContext):
    query = update.callback_query
    query.message.delete()

def cashback_details_handler(update: Update, context: CallbackContext):
    query = update.callback_query

    limit = 25
    current_page = 0
    response = get_cashbacks(status_id=0, limit=limit, page=current_page)
    cashbacks_data = response.json()["data"]

    cashback = None



    if query.data.startswith("cashback_details_"):
        item_id = query.data.replace("cashback_details_", "")
        items = cashbacks_data["data"]


        try:
            item_id = int(item_id)


            for item in items:
                compare_id = int(item["id"])
                if compare_id == item_id:
                    cashback = item
                    global CASHBACK_ID
                    CASHBACK_ID = item["cashbackItems"][0]["id"]
                    break
                else:
                    continue

            if cashback and CASHBACK_ID is not None:
                CASHBACK_ID = int(CASHBACK_ID)
                text = "Полные данные о кэшбеке:\n"
                photo = cashback['photo']
                text += f"Название акции: {cashback['name']}\n"
                text += f"Описание: {cashback['publishText']}\n"
                text += f"Длительность акции: {cashback['daysAction']} (день/дня/дней)\n"
                text += f"Процент кэшбека: {cashback['cashbackPercentage']}%\n"                

                buttons = [
                        InlineKeyboardButton("Участвовать", callback_data=f"cashback_details_{item_id}_participate"),
                        InlineKeyboardButton("Назад", callback_data=f"cashback_details_{item_id}_not_participate")
                    ]
                keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2))


                query.message.reply_photo(photo, caption=text, reply_markup=keyboard)
            else:
                print("Invalid item_id")
        except ValueError:
            print("Invalid item_id")        
    else:
        print("Invalid query data format")


    if query.data.endswith("_not_participate"):
        delete_message(update, context)

    elif query.data.endswith("_participate"):
        if CASHBACK_ID is not None:
            tg_id = update.effective_user.id
            user_id = get_tg_id(tg_id).json()["data"]["id"]

            cashbackItemId = CASHBACK_ID

            cashbackUserId = user_id

            response = add_to_my_cashbacks(cashbackItemId, cashbackUserId)
            delete_message(update, context)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=f'Поздравляем! Вы участвуете в кэшбеке. для выполнения условий перейдите в меню "Мои активные кэшбеки" и выберите там кэшбек, для которого будете выполнять условия')
