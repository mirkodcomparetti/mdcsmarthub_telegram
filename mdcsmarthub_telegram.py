#!/usr/bin/python3
"""
Simple Bot to handle the MDC SmartHome
"""
import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import paho.mqtt.publish as publish
from paho import mqtt
import uuid
from rfc3986 import urlparse
import pytz
import json
from influxdb_client import InfluxDBClient, Point, Dialect


class TelegramBotCore:
    """TelegramBotCore app."""

    def __init__(self, mqtt_client, db_client):
        """Init TelegramBotCore class."""
        self.logger = logging.getLogger("mdcsmarthub_telegram" + ".TelegramBotCore")
        self.logger.info("Begin initialize class TelegramBotCore")
        self.mqtt_instance = mqtt_client
        self.db_instance = db_client
        # self.logger.debug("Capturing signals")
        # signal.signal(signal.SIGINT, self._cleanup)
        # signal.signal(signal.SIGTERM, self._cleanup)

        self.updater = Updater(os.getenv('MDCSMARTHUB_TELEGRAM_API', None), use_context=True)
        # Get the dispatcher to register handlers
        self.dispatcher = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dispatcher.add_handler(CommandHandler("start", self._start))
        self.dispatcher.add_handler(CommandHandler("help", self._help))
        self.dispatcher.add_handler(CommandHandler("ledwall", self._ledwall))
        self.dispatcher.add_handler(CommandHandler("lastdata", self._lastdata))
        # on noncommand i.e message - echo the message on Telegram
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self._generic))

        self.allowedchatids = [i for i in os.environ.get('MDCSMARTHUB_TELEGRAM_CHATID').split(" ")]

        self.logger.info("Done initialize class TelegramBotCore")

    def _cleanup(self, signum, frame):
        self.logger.debug("Cleanup")

    def _check_chat_id(self, update: Update) -> False:
        """Check if the chat id is approved."""
        return str(update.message.chat.id) in self.allowedchatids

    def _refuse(self, update: Update):
        """Check if the chat id is approved."""
        self.logger.debug("Refuse message")
        update.message.reply_markdown(
            'Your user was not identified.\n\n'
            'There is nothing here to do for you.'
        )

    def _start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        self.logger.debug("Running start action")
        if not self._check_chat_id(update):
            self._refuse(update)
            return
        update.message.reply_markdown(
            'Welcome in the _MDC SmarthHub_ telegram Bot.\n\n'
            'With this bot you can get information about your subscriptions to our service.\n\n'
            'You can always type /help to see what you can do.'
        )

    def _help(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        self.logger.debug("Running help action")
        if not self._check_chat_id(update):
            self._refuse(update)
            return
        update.message.reply_markdown(
            'Possible commands are:\n- /ledwall: write last speedtest data on LED wall\n- /lastdata: respond with '
            'last speedtest data.')

    def _ledwall(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /ledwall is issued."""
        self.logger.debug("Running ledwall action")
        if not self._check_chat_id(update):
            self._refuse(update)
            return
        update.message.reply_markdown('Sending message on ledwall')
        resultdata = self.db_instance.get_last_data()
        msg = {
            "ledwall": 'D {} - U {} - P {}'.format(resultdata["DownloadBandwidth"], resultdata["UploadBandwidth"],
                                                   resultdata["PingLatency"])
        }
        self.mqtt_instance.send_message(msg)

    def _lastdata(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /lastdata is issued."""
        self.logger.debug("Running lastdata action")
        if not self._check_chat_id(update):
            self._refuse(update)
            return
        resultdata = self.db_instance.get_last_data()
        local_tz = pytz.timezone("Europe/Rome")
        resultdatatime = resultdata["time"].astimezone(local_tz).strftime("%d/%m/%Y@%H:%M:%S")
        update.message.reply_markdown('Here you can find your last speedtest data:\n- When: {}\n- Download: {}Mbps\n- '
                                      'Upload: {}Mbps\n- Ping: {}ms'.format(resultdatatime, resultdata[
            "DownloadBandwidth"], resultdata["UploadBandwidth"], resultdata["PingLatency"]))

    def _generic(self, update: Update, context: CallbackContext) -> None:
        """Generic reponse to a message."""
        self.logger.debug("Running generic action")
        if not self._check_chat_id(update):
            self._refuse(update)
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


class MqttClientCore:
    """Main app."""

    def __init__(self):
        """Init MqttClientCore class."""
        self.logger = logging.getLogger("mdcsmarthub_telegram" + ".MqttClientCore")
        self.logger.info("Begin initialize class MqttClientCore")
        topic_prefix = os.environ.get('MDCSMARTHUB_MQTT_TOPIC_PREFIX', "telegrambot")
        self.topic_prefix = topic_prefix if topic_prefix.endswith("/") else (topic_prefix + "/")
        self.broker_url = None
        self.broker_port = None
        self.broker_user = None
        if not self._validate_info(os.environ.get('MDCSMARTHUB_MQTT_BROKER', "mqtt://test.mosquitto.org:1883")):
            self.logger.error("Broker information not valid")
            return

        self.logger.info("Done initialize class MqttClientCore")

    def _validate_info(self, broker_info) -> False:
        self.logger.debug("Validating " + broker_info)
        parseduri = urlparse(broker_info)
        if not (parseduri.scheme in ["mqtt", "ws"]):
            return False
        self.broker_url = parseduri.host
        self.broker_port = parseduri.port
        self.broker_user = parseduri.userinfo
        self.logger.debug("broker_user {}".format(self.broker_user))
        self.logger.debug("broker_url {}, broker_port: {}".format(self.broker_url, self.broker_port))
        if not (self.broker_url and self.broker_port):
            return False
        return True

    def send_message(self, json_message):
        self.logger.debug("MQTT send message")
        publish.single(self.topic_prefix + "commands", payload=json.dumps(json_message), qos=0, retain=False,
                       hostname=self.broker_url, port=self.broker_port, client_id=str(uuid.uuid4()), keepalive=60,
                       will=None, auth=None, tls=None, transport="tcp")


class DbConnector:
    """DbConnector class."""

    def __init__(self) -> None:
        """Init DbConnector class."""
        self.logger = logging.getLogger("mdcsmarthub_telegram" + ".DbConnector")
        self.logger.info("Begin initialize class DbConnector")
        self.url = None
        self.measurement = os.environ.get('MDCSMARTHUB_DB_MEASUREMENT')
        self.bucket = os.environ.get('MDCSMARTHUB_DB_BUCKET')
        self.org = os.environ.get('MDCSMARTHUB_DB_ORG')
        self.token = os.environ.get('MDCSMARTHUB_DB_TOKEN')
        if not self._validate_info(os.environ.get('MDCSMARTHUB_DB_URL', 'http://localhost:8086')):
            return

        self.query_string = 'import "math" \
            from(bucket: "' + self.bucket + '") \
              |> range(start: -1d) \
              |> filter(fn: (r) => r["_measurement"] == "' + self.measurement + '" and ( \
                r[\"_field\"] == \"DownloadBandwidth\" or \
                r[\"_field\"] == \"UploadBandwidth\" or \
                r[\"_field\"] == \"PingLatency\")\
              ) \
              |> last() \
              |> group() \
              |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value") \
              |> keep(columns: ["_time", "DownloadBandwidth", "UploadBandwidth", "PingLatency"]) \
              |> map(fn: (r) => ({ r with DownloadBandwidth: math.round(x: (r.DownloadBandwidth * 8.0 / 10000.0)) / 100.0 })) \
              |> map(fn: (r) => ({ r with UploadBandwidth: math.round(x: (r.UploadBandwidth * 8.0 / 10000.0)) / 100.0 }))'
        self.logger.info("Done initialize class DbConnector")

    def _validate_info(self, broker_info) -> False:
        self.logger.info("Validating " + broker_info)
        parsed_uri = urlparse(broker_info)
        if not (parsed_uri.scheme in ["http", "https"]):
            return False
        if not parsed_uri.host:
            return False
        self.url = "{}://{}".format(parsed_uri.scheme,
                                    parsed_uri.host if not parsed_uri.port else "{}:{}".format(parsed_uri.host,
                                                                                               parsed_uri.port))
        if not (self.url and self.bucket and self.org and self.token and self.measurement):
            return False
        self.logger.debug(
            "url {}, org: {}, bucket: {}, measurement: {}, token: {}".format(self.url, self.org, self.bucket,
                                                                             self.measurement, self.token))
        return True

    def get_last_data(self) -> None:
        db_client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

        db_data = db_client.query_api().query_stream(query=self.query_string, org=self.org)
        out_data = {}
        for record in db_data:
            self.logger.debug(
                f'Time {record["_time"]} Down {record["DownloadBandwidth"]}, UploadBandwidth {record["UploadBandwidth"]}, Ping {record["PingLatency"]}')
            out_data = record.values
            out_data["time"] = out_data.pop("_time")
            del out_data["result"]
            del out_data["table"]
        self.logger.debug(out_data)

        db_client.__del__()

        return out_data


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
    mqtt_instance = MqttClientCore()
    db_instance = DbConnector()
    bot_instance = TelegramBotCore(mqtt_instance, db_instance)
    logger.info("Run main bot loop - wait for stop signal")
    bot_instance.loop()
    logger.info("Stopping main loop")
