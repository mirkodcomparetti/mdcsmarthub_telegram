# MDC SmartHub Telegram Bot

## Introduction

The files here create a service that implements a _telegram bot_ that queries your [influxdb](https://influxdata.com/) database to gather the latest speedtest data.

This service is tested on the Raspberry Pi 2 with Raspberry Pi OS light, but it should work on all hardware and OSs that based on unit files.

## Folder structure

The files are here structured in this way:

* `mdcsmarthub_telegram.py` python script to read handle the bot operations
* `mdcsmarthub_telegram.logrotate` configuration for [logrotate](https://manpages.debian.org/stretch/logrotate/logrotate.8.en.html) to rotate the log file of this script
* `mdcsmarthub_telegram.env` file to define the environmental variables used while running the background service
* `mdcsmarthub_telegram.service` file to run the background service
* `setconfiguration.sh` script to configure the system and properly propagate the files in the right folders

## How-to

The main python script `mdcsmarthub_telegram.py` does the following operations when it runs:
* Responds to the bot operations only for the chat ids listed in the proper environment variable
* Connects to and queries the DB to get the data
* Publish data on the mqtt broker

The script logs its operations in the file `/var/log/mdc/smarthub_telegram.log`.

The script requires a configuration through environmental variables defined in the `mdcsmarthub_telegram.env` file.
The available configuration parameters are:
* `MDCSMARTHUB_TELEGRAM_API="<bot api>"` telegram bot API token
* `MDCSMARTHUB_TELEGRAM_CHATID="<desired chat id filter>"`
* `MDCSMARTHUB_TELEGRAM_LOGLEVEL="<desired level>"` the desired log level to be used in the log, as defined by the [python library](https://docs.python.org/3/library/logging.html#levels)
* `MDCSMARTHUB_MQTT_BROKER="<broker>"` endpoint of the broker
* `MDCSMARTHUB_MQTT_TOPIC_PREFIX="<topic>"` to set the prefix for all the topics (default `sensehat`): `readings` is used for the readings and `commands` to process input commands
* `MDCSMARTHUB_DB_URL="<url>"` influxdb2 endpoint url
* `MDCSMARTHUB_DB_ORG="<org>"` influxdb2 organization
* `MDCSMARTHUB_DB_TOKEN="<token>"` influxdb2 API token
* `MDCSMARTHUB_DB_BUCKET="<bucket>"` influxdb2 bucket
* `MDCSMARTHUB_DB_MEASUREMENT="<measurement>"` measurement name

## Deploy

In order to deploy the configuration, you need to do the following steps

1. Run the file `zip.bat`
1. Transfer the zip file `mdcsmarthub_telegram_*.zip` to the desired target machine
1. On the target machine, extract the zip file content
1. run the following command
	```
	<sudo> bash ./setconfiguration.sh
	```

After this has been successfully executed the new service is already running, and it can be managed using

	<sudo> systemctl <command> mdcsmarthub_telegram.service