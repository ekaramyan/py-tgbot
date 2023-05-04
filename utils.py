from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import logging
import requests

HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

URL = "http://62.217.183.218:8000/api"

def register_user(password: str, roleId: str, photo: str, firstName: str, lastName: str, email: str, login: str, phone: str, tg: str):

    HEADERS['token'] = ''
    json_data = {
        'password': password,
        'roleId': 0,
        'photo': photo,
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'login': login,
        'phone': phone,
        'tg': tg,
    }

    response = requests.post(URL + '/users', headers=HEADERS, json=json_data)

    return response

def get_cashbacks(status_id: int, limit: int, page: int):

    params = {
        'status_id': status_id,
        'limit': limit,
        'page': page,
    }

    response = requests.get(URL + '/cashbacks', params=params, headers=HEADERS)

    return response

def cashbacks_users_history(id: int, limit: int, page: int):
    
    params = {
        'limit': limit,
        'page': page,
    }

    response = requests.get(URL + '/cashbacks/users/{0}/history'.format(id), params=params, headers=HEADERS)

    return response


print(register_user('test', 0, 'test', 'test1', 'test2', 'test@gmail.com', 'test', '3456789', 'test').text)


url = ''
files = {'media': open(r'C:\Programming\work\py-tgbot\test.jpg.jpg', 'rb')}

print(requests.post(url, files=files))


# заглушка для отправки запроса к API


def request_data(update: Update, context: CallbackContext, data_type):
    logging.info(f"request_data called with data_type={data_type}")
    pass

# заглушка для отмены запроса к API


def cancel_request_data(context: CallbackContext):
    chat_id, message_id = context.job.context
    logging.info(
        f"cancel_request_data called for chat_id={chat_id}, message_id={message_id}")
    context.bot.send_message(
        chat_id=chat_id, text="Время ожидания истекло. Попробуйте еще раз.")


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons] if not isinstance(
            header_buttons, list) else header_buttons)
    if footer_buttons:
        menu.append([footer_buttons] if not isinstance(
            footer_buttons, list) else footer_buttons)
    return menu
