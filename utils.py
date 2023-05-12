from typing import List
from telegram import Update
from telegram.ext import CallbackContext
import logging
import requests
import pathlib


HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

URL = 'http://62.217.183.218:8000/api'


def register_user(firstName: str, lastName: str, middleName: str, phoneNumber: str, creditCartNumber: str, tgNickname: str, bannedText: str):

    json_data = {
        'firstName': firstName,
        'lastName': lastName,
        'middleName': middleName,
        'phoneNumber': phoneNumber,
        'creditCartNumber': creditCartNumber,
        'tgNickname': tgNickname,
        'isBanned': False,
        'bannedText': bannedText,
    }

    response = requests.post(URL + '/cashbacks/users',
                             headers=HEADERS, json=json_data)

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

    response = requests.get(
        URL + '/cashbacks/users/{0}/history'.format(id), params=params, headers=HEADERS)

    return response


def request_files(id: int, condition: int, path_file: str):

    headers = {
        'accept': 'application/json',
        # 'Content-Type': 'multipart/form-data'
    }
    params = {
        'condition': condition,
    }
    
    files = {
        'file': open(path_file, 'rb'),
    }
    response = requests.patch(URL + '/cashbacks/actions/{0}/upload'.format(id), params=params, headers=headers, files=files)

    return response


def get_tg_nickname(tg_nickname: str):

    headers = {
        'accept': 'application/json',
    }
    response = requests.get(URL + '/cashbacks/users/{0}'.format(tg_nickname), headers=headers)

    return response



# добавь эндпоинт для отправки кэшбека в список кэшбеков пользователя

def add_to_my_cashbacks(cashback_id: int):
    payload = {
        'id': cashback_id,
    }

    response = requests.post(URL + '/cashbacks/contracts', json=payload, headers=HEADERS)
    return response.json()

# написал все же сам, но я в нем не уверен


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
