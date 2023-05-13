from typing import List
<<<<<<< HEAD
from telegram import Update
=======
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
>>>>>>> main
from telegram.ext import CallbackContext
import logging
import requests

<<<<<<< HEAD

=======
>>>>>>> main
HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

<<<<<<< HEAD
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
=======
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

>>>>>>> main
    params = {
        'status_id': status_id,
        'limit': limit,
        'page': page,
    }

    response = requests.get(URL + '/cashbacks', params=params, headers=HEADERS)
<<<<<<< HEAD
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



def my_cashbacks(user_id: int, limit: int, page: int):

=======

    return response

def cashbacks_users_history(id: int, limit: int, page: int):
    
>>>>>>> main
    params = {
        'limit': limit,
        'page': page,
    }

<<<<<<< HEAD
    response = requests.get(URL + '/cashbacks/{0}/contracts'.format(user_id), params=params, headers=HEADERS)
    return response.json()


def add_to_my_cashbacks(cashbackActionId: int, cashbackItemId: int, cashbackUserId: int, cashbackContractStatusId: int):

    print(cashbackUserId)
    print(cashbackItemId)

    params = {
        'cashbackActionId': cashbackActionId,
        'cashbackItemId': cashbackItemId,
        'cashbackUserId': cashbackUserId,
        'cashbackContractStatusId': cashbackContractStatusId,

        'userPaid': True,
        'userStartedAt': '2023-05-12T07:07:09.044Z',
        'hasComplited': True,
        'hasPaid': True,
        'paidDocumentUrl': 'string',
        'isCondition1': True,
        'condition1Url': 'string',
        'condition1Hours': 0,
        'condition1FinishedAt': '2023-05-12T07:07:09.044Z',
        'isCondition1CheckedByAdmin': True,
        'isCondition2': True,
        'condition2Url': 'string',
        'condition2Hours': 0,
        'condition2FinishedAt': '2023-05-12T07:07:09.044Z',
        'isCondition2CheckedByAdmin': True,
        'isCondition3': True,
        'condition3Url': 'string',
        'condition3Hours': 0,
        'condition3FinishedAt': '2023-05-12T07:07:09.044Z',
        'isCondition3CheckedByAdmin': True,
        'isCondition4': True,
        'condition4Url': 'string',
        'condition4Hours': 0,
        'condition4FinishedAt': '2023-05-12T07:07:09.044Z',
        'isCondition4CheckedByAdmin': True,
        'isCondition5': True,
        'condition5Url': 'string',
        'condition5Hours': 0,
        'condition5FinishedAt': '2023-05-12T07:07:09.044Z',
        'isCondition5CheckedByAdmin': True,
    }

    response = requests.post(URL + '/cashbacks/contracts', json=params, headers=HEADERS)
    return response.json()

=======
    response = requests.get(URL + '/cashbacks/users/{0}/history'.format(id), params=params, headers=HEADERS)

    return response


print(register_user('test', 0, 'test', 'test1', 'test2', 'test@gmail.com', 'test', '3456789', 'test').text)


url = ''
files = {'media': open(r'C:\Programming\work\py-tgbot\test.jpg.jpg', 'rb')}

print(requests.post(url, files=files))


# заглушка для отправки запроса к API
>>>>>>> main


def request_data(update: Update, context: CallbackContext, data_type):
    logging.info(f"request_data called with data_type={data_type}")
    pass

<<<<<<< HEAD

=======
>>>>>>> main
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
