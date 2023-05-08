import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from handlers import start, button_callback, register_handler
from cashback_buttons import available_cashbacks_handler
from menu import receive_cashback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '6134723312:AAFy2KiaQZQQdtDQL66OrZRs8QmBSAm1wxk'

updater = Updater(token=TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))

conv_handler = register_handler()
updater.dispatcher.add_handler(conv_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(
    available_cashbacks_handler, pattern="available_cashbacks"))


updater.dispatcher.add_handler(MessageHandler(Filters.text, receive_cashback))

updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))


updater.start_polling()

updater.idle()
