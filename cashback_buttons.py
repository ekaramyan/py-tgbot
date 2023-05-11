from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, build_menu, cashbacks_users_history
import math

def available_cashbacks_handler(update: Update, context: CallbackContext):
    limit = 15  # количество элементов на странице
    current_page = 0
    response = get_cashbacks(status_id=0, limit=limit, page=current_page)
    cashbacks_data = response.json()["data"]

    items = cashbacks_data["data"]
    total_pages = cashbacks_data["total_pages"]
    prefix = "cashback"

    # Сохранение items в user_data
    context.user_data["cashback_items"] = items
    context.user_data["cashback_total_pages"] = total_pages

    send_pagination(update, context, items, current_page, total_pages, prefix, limit)


def get_user_cashbacks(id: int, limit: int, page: int):
    response = cashbacks_users_history(id, limit, page)
    cashbacks_data = response.json()["data"]
    items = cashbacks_data["data"]
    total_pages = cashbacks_data["total_pages"]
    return items, total_pages


def send_pagination(update, context, items, current_page, total_pages, prefix, limit):
    if len(items) == 0:
        update.message.reply_text("Нет доступных элементов")
        return

    start_index = current_page * limit
    end_index = start_index + limit

    items_slice = items[start_index:end_index]
    buttons = []

    for i, item in enumerate(items_slice):
        item_id = start_index + i
        item_name = item["name"]
        buttons.append(InlineKeyboardButton(str(item_name), callback_data=f"{prefix}_{item_id}"))

    if current_page > 0:
        buttons.append(InlineKeyboardButton("<< Назад", callback_data=f"{prefix}_prev"))
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед >>", callback_data=f"{prefix}_next"))

    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=1))
 
    if "message_id" in context.user_data:
        # Обновление существующего сообщения
        message_id = context.user_data["message_id"]
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="Доступные элементы:",
            reply_markup=keyboard
        )
    else:
        # Отправка нового сообщения
        message = update.message.reply_text("Доступные элементы:", reply_markup=keyboard)
        context.user_data["message_id"] = message.message_id

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
    print('sheesh')

    query = update.callback_query
    prefix, action = query.data.split("_")

    # Получение текущей страницы из user_data
    current_page = int(context.user_data.get(f"{prefix}_page", 0))

    if action == "prev":
        current_page -= 1  
    elif action == "next":
        current_page += 1

    # Получение items из user_data
    items = context.user_data.get("cashback_items", [])  

    # Получение limit из user_data
    limit = 5

    # Сохранение нового значения текущей страницы в user_data
    context.user_data[f"{prefix}_page"] = current_page
    print(current_page)
    get_pagination(update, context, items, prefix, current_page, limit)