from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, build_menu, cashbacks_users_history, my_cashbacks, get_tg_id

# ff

    # items = my_cashbacks(user_id: user_id, limit: limit, page: current_page).json()["data"]

def available_cashbacks_handler(update: Update, context: CallbackContext, status_id: int, show_text: bool):
    limit = 25
    current_page = 0
    response = get_cashbacks(status_id=status_id, limit=limit, page=current_page)
    cashbacks_data = response.json()["data"]

    items = cashbacks_data["data"]
    total_pages = cashbacks_data["total_pages"]
    prefix = "cashback"


    context.user_data["cashback_items"] = items
    context.user_data["cashback_total_pages"] = total_pages

    send_pagination(update, context, items, current_page, total_pages, prefix, limit, new_message=True, show_text=show_text)


def get_user_cashbacks(update: Update, context: CallbackContext):
    limit = 25
    current_page = 0
    tg_id = update.effective_user.id
    user_id = get_tg_id(tg_id).json()["data"]["id"]

    response = my_cashbacks(user_id, limit=limit, page=current_page)
    cashbacks_data = response["data"]
    items = cashbacks_data["data"]
    total_pages = cashbacks_data["total_pages"]
    prefix = "cashback_history"

    context.user_data["cashback_history_items"] = items
    context.user_data["cashback_history_total_pages"] = total_pages

    send_pagination(update, context, items, current_page, total_pages, prefix, limit, new_message=True, show_text=False)

def send_pagination(update, context, items, current_page, total_pages, prefix, limit, new_message=False, show_text=False):
    if len(items) == 0:
        message = update.message.reply_text("Это меню пустое")
        context.user_data["message_id"] = message.message_id
        return

    start_index = current_page * limit
    end_index = start_index + limit

    items_slice = items[start_index:end_index]
    buttons = []

    for i, item in enumerate(items_slice):
        print(item)
        item_id = item["id"]
        if(prefix == 'cashback'):
            item_name = item["name"]            
            buttons.append(InlineKeyboardButton(str(item_name), callback_data=f"cashback_details_{item_id}"))
        elif(prefix == 'cashback_history'):
            item_name = item["cashbackAction"]["name"]
            buttons.append(InlineKeyboardButton(str(item_name), callback_data=f"cashback_aproval_{item_id}"))

    if current_page > 0:
        buttons.append(InlineKeyboardButton("<< Назад", callback_data=f"{prefix}_prev"))
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед >>", callback_data=f"{prefix}_next"))

    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=1))

    if new_message or "message_id" not in context.user_data:
        if show_text:
            text = "\n".join([item["name"] for item in items_slice])
            message = update.message.reply_text('Архивные кэшбеки:\n' + text)
            context.user_data["message_id"] = message.message_id
        else:
            message = update.message.reply_text("Доступные кэшбеки:", reply_markup=keyboard)
            context.user_data["message_id"] = message.message_id
    else:
        if show_text:
            message_id = context.user_data["message_id"]
            text = "\n".join([item["name"] for item in items_slice])
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard
            )
        else:
            message_id = context.user_data["message_id"]
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text="Доступные кэшбеки:",
                reply_markup=keyboard
            )


def get_pagination(update, context, items, prefix, page, limit):
    total_pages = context.user_data.get("cashback_total_pages", 0)

    if page < 0 or page >= total_pages:
        # Недопустимая страница, не делать запрос
        return

    response = get_cashbacks(status_id=0, limit=limit, page=page)
    cashbacks_data = response.json()["data"]
    items = cashbacks_data["data"]

    context.user_data["cashback_items"] = items

    send_pagination(update, context, items, page, total_pages, prefix, limit)


def pagination_handler(update: Update, context: CallbackContext):
    items = context.user_data.get("cashback_items", [])
    if len(items) == 0:
        if update.message:
            message = update.message.reply_text("Тут ничего нет:(")
            context.user_data["message_id"] = message.message_id
        return   
    query = update.callback_query
    prefix, action = query.data.split("_")
    current_page = int(context.user_data.get(f"{prefix}_page", 0))

    if action == "prev":
        current_page -= 1
    elif action == "next":
        current_page += 1

    limit = 25
    total_pages = context.user_data.get("cashback_total_pages", 0)
    context.user_data[f"{prefix}_page"] = current_page

    send_pagination(update, context, items, current_page, total_pages, prefix, limit)



def cashbacks_archive_handler(update: Update, context: CallbackContext):
    context.user_data["cashback_status_id"] = 1
    available_cashbacks_handler(update, context, status_id=1, show_text=True)

def cashbacks_available_handler(update: Update, context: CallbackContext):
    context.user_data["cashback_status_id"] = 0
    available_cashbacks_handler(update, context, status_id=0, show_text=False)