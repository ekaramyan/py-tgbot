import logging
<<<<<<< HEAD
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from handlers import start, button_callback, register_handler
from cashback_buttons import cashbacks_available_handler, pagination_handler, get_user_cashbacks, cashbacks_archive_handler
from add_cashback import cashback_details_handler
from menu import receive_cashback
from aprove_cashback import cashback_aprove_handler
=======
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from handlers import start, receive_cashback, button_callback, register_phone
>>>>>>> main

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

<<<<<<< HEAD
TOKEN = '6134723312:AAFy2KiaQZQQdtDQL66OrZRs8QmBSAm1wxk'
=======
TOKEN = '6175697143:AAE7yRI7PegZ2mR0Jj2-Ph2l8r6k5bcaDQA'
>>>>>>> main

updater = Updater(token=TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))

<<<<<<< HEAD
conv_handler = register_handler()
updater.dispatcher.add_handler(conv_handler)

updater.dispatcher.add_handler(MessageHandler(Filters.regex(
    '^(Доступные кэшбеки)$'), cashbacks_available_handler))

updater.dispatcher.add_handler(MessageHandler(Filters.regex(
    '^(Архивные кэшбеки)$'), cashbacks_archive_handler))

updater.dispatcher.add_handler(MessageHandler(Filters.regex(
    '^(Ваши кэшбеки)$'), get_user_cashbacks))

updater.dispatcher.add_handler(CallbackQueryHandler(cashback_details_handler, pattern=r"^cashback_details_.*"))

updater.dispatcher.add_handler(CallbackQueryHandler(cashback_aprove_handler, pattern=r"^cashback_aproval_.*"))

updater.dispatcher.add_handler(CallbackQueryHandler(pagination_handler, pattern=r"^(cashback|other)_.*"))

=======
>>>>>>> main
updater.dispatcher.add_handler(MessageHandler(Filters.text, receive_cashback))

updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))

<<<<<<< HEAD

=======
updater.dispatcher.add_handler(MessageHandler(
    Filters.regex(r"^\d$"), register_phone))
>>>>>>> main


updater.start_polling()

updater.idle()
