#!/usr/bin/python3
"""
Simple Bot to handle the MDC SmartHome
"""
import json
import os
import logging
import signal
from telegram import Update, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext


class TelegramBotCore:
    """Main app."""

    def __init__(self):
        """Init TelegramBotCore class."""
        self.logger = logging.getLogger("mdcsmarthub_telegram" + ".TelegramBotCore")
        self.logger.info("Begin initialize class TelegramBotCore")
        # self.logger.debug("Capturing signals")
        # signal.signal(signal.SIGINT, self.cleanup)
        # signal.signal(signal.SIGTERM, self.cleanup)

        self.updater = Updater(os.getenv('MDCSMARTHUB_TELEGRAM_API', None), use_context=True)
        # Get the dispatcher to register handlers
        self.dispatcher = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("ledwall", self.ledwall))
        self.dispatcher.add_handler(CommandHandler("lastdata", self.lastdata))
        # on noncommand i.e message - echo the message on Telegram
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.generic))

        self.allowedchatids = [i for i in os.environ.get('MDCSMARTHUB_TELEGRAM_CHATID').split(" ")]

    def cleanup(self, signum, frame):
        self.logger.debug("Cleanup")

    def check_chat_id(self, update: Update) -> False:
        """Check if the chat id is approved."""
        return str(update.message.chat.id) in self.allowedchatids

    def refuse(self, update: Update):
        """Check if the chat id is approved."""
        self.logger.debug("Refuse message")
        update.message.reply_markdown(
            'Your user was not identified.\n\n'
            'There is nothing here to do for you.'
        )

    def start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        self.logger.debug("Running start action")
        if not self.check_chat_id(update):
            self.refuse(update)
            return
        update.message.reply_markdown(
            'Welcome in the _MDC SmarthHub_ telegram Bot.\n\n'
            'With this bot you can get information about your subscriptions to our service.\n\n'
            'You can always type /help to see what you can do.'
        )

    def help(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        self.logger.debug("Running help action")
        if not self.check_chat_id(update):
            self.refuse(update)
            return
        update.message.reply_markdown(
            'Possible commands are:\n- /ledwall: write on ledwall\n- /lastdata: write lastdata.')

    def ledwall(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /ledwall is issued."""
        self.logger.debug("Running ledwall action")
        if not self.check_chat_id(update):
            self.refuse(update)
            return
        update.message.reply_markdown('Working on ledwall')

    def lastdata(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /lastdata is issued."""
        self.logger.debug("Running lastdata action")
        if not self.check_chat_id(update):
            self.refuse(update)
            return
        update.message.reply_markdown('Working on lastdata')

    def generic(self, update: Update, context: CallbackContext) -> None:
        """Generic reponse to a message."""
        self.logger.debug("Running generic action")
        if not self.check_chat_id(update):
            self.refuse(update)
            return
        update.message.reply_markdown(
            'I appreciate you sending a message to me...\nI do not know how to handle it though, as I only know how to '
            'respond to commands. Try /help to see what you can do.')

    def loop(self) -> None:
        """Start the bot."""
        self.logger.debug("Looping in the bot")

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()


# Enable logging
logging.basicConfig(
    # filename='/var/log/mdc/mdcsmarthub_telegram.log',
    format='%(asctime)s.%(msecs)03d %(levelname)s\t[%(name)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger("mdcsmarthub_telegram")
logger.setLevel(os.environ.get('MDCSMARTHUB_TELEGRAM_LOGLEVEL', logging.INFO))

if __name__ == "__main__":
    # Start MDCSmartHub Telegram app
    logger.info("Starting MDCSmartHub Telegram service")
    root = TelegramBotCore()
    logger.info("Run main loop - wait for stop signal")
    root.loop()
    logger.info("Stopping main loop")
