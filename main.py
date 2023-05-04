import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from handlers import start, receive_cashback, button_callback, register_phone

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '6134723312:AAFy2KiaQZQQdtDQL66OrZRs8QmBSAm1wxk'

updater = Updater(token=TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))

updater.dispatcher.add_handler(MessageHandler(Filters.text, receive_cashback))

updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))

updater.dispatcher.add_handler(MessageHandler(
    Filters.regex(r"^\d$"), register_phone))


updater.start_polling()

updater.idle()
