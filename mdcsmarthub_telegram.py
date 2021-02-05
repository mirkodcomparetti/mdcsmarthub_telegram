#!/usr/bin/python3
"""
Simple Bot to handle the MDC SmartHome
"""

import os
import logging
import signal
from telegram import Update, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext


class TelegramBotCore:
    """Main app."""

    def __init__(self):
        """Init RpiSenseHatMqtt class."""
        self.logger = logging.getLogger('rpi_broadcaster.RpiSenseHatMqtt')
        self.logger.info("Begin initialize class RpiSenseHatMqtt")
        # self.logger.debug("Capturing signals")
        # signal.signal(signal.SIGINT, self.cleanup)
        # signal.signal(signal.SIGTERM, self.cleanup)

        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(os.getenv('MDC_SMARTHUB_TELEGRAM_API', None), use_context=True)
        # Get the dispatcher to register handlers
        self.dispatcher = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("ledwall", self.ledwall))
        self.dispatcher.add_handler(CommandHandler("lastdata", self.lastdata))

        # on noncommand i.e message - echo the message on Telegram
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.generic))

    def cleanup(self, signum, frame):
        self.logger.debug("Cleanup")

    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.
    def start(self, context: CallbackContext):
        """Send a message when the command /start is issued."""
        self.logger.debug("start")
        self.update.message.reply_markdown(
            'Welcome in the _MDC SmarthHub_ telegram Bot.\n\n'
            'With this bot you can get information about your subscriptions to our service.\n\n'
            'You can always type /help to see what you can do.'
        )

    def help(self, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        self.logger.debug("help")
        self.update.message.reply_markdown(
            'Possible commands are:\n- /ledwall: write on ledwall\n- /lastdata: write lastdata.')

    def ledwall(self, context: CallbackContext) -> None:
        """Send a message when the command /ledwall is issued."""
        self.logger.debug("ledwall")
        self.update.message.reply_markdown('Working on ledwall')

    def lastdata(self, context: CallbackContext) -> None:
        """Send a message when the command /lastdata is issued."""
        self.logger.debug("lastdata")
        self.update.message.reply_markdown('Working on lastdata')

    def generic(self, update: Update, context: CallbackContext) -> None:
        """Generic reponse to a message."""
        self.logger.debug("generic")
        self.update.message.reply_markdown(
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
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('MDC_SMARTHUB_TELEGRAM_LOGLEVEL', logging.INFO))

if __name__ == "__main__":
    # Start MDCSmartHub Telegram app
    logger.info("Starting MDCSmartHub Telegram service")
    root = TelegramBotCore()
    logger.info("Run main loop - wait for stop signal")
    root.loop()
    logger.info("Stopping main loop")
