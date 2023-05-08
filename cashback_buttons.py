from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from utils import get_cashbacks, build_menu


def send_cashbacks(update: Update, context: CallbackContext, cashbacks: list[str], current_page: int):
    print('send works')
    if len(cashbacks) == 0:
        update.message.reply_text("Нет доступных кэшбеков")
        return

    items_per_page = 5
    start_index = current_page * items_per_page
    end_index = (current_page + 1) * items_per_page

    text = "Доступные кэшбеки:\n\n" + \
        "\n".join(cashbacks[start_index:end_index])

    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(
            "<< Назад", callback_data=f"available_cashbacks_{current_page - 1}"))
    if end_index < len(cashbacks):
        buttons.append(InlineKeyboardButton("Вперед >>",
                       callback_data=f"available_cashbacks_{current_page + 1}"))

    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=1))
    update.message.reply_text(text, reply_markup=keyboard)

def available_cashbacks_handler(update: Update, context: CallbackContext):
    print('ach works')
    limit = 10  # количество элементов на странице
    current_page = 0
    response = get_cashbacks(status_id=1, limit=limit, page=current_page)
    cashbacks = [cashback["name"] for cashback in response.json()["data"]]
    send_cashbacks(update, context, cashbacks, current_page)


