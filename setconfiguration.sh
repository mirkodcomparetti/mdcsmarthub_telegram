#!/bin/bash

get_ack() {
	# https://djm.me/ask
	local prompt default reply

	while true; do
		if [ "${2:-}" = "Y" ]; then
			prompt="Y/n"
			default=Y
		elif [ "${2:-}" = "N" ]; then
			prompt="y/N"
			default=N
		else
			prompt="y/n"
			default=
		fi

		# Ask the question (not using "read -p" as it uses stderr not stdout)
		echo -n "$1 [$prompt] "
		# Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
		read reply </dev/tty

		# Default?
		if [ -z "$reply" ]; then
			reply=$default
		fi
		# Check if the reply is valid
		case "$reply" in
			Y*|y*)
				return 0;;
			N*|n*)
				return 1;;
		esac
	done
}

echo "mdcsmarthub_telegram configuration for RevPi";
if [ "$EUID" -ne 0 ]; then
	echo "Please run as root or sudo"
	exit
fi

echo "This script assumes the configuration is saved in the same folder as this script ";
echo "Required files:";
echo "- mdcsmarthub_telegram.py";
echo "- mdcsmarthub_telegram.logrotate";
echo "- mdcsmarthub_telegram.env";
echo "- mdcsmarthub_telegram.service";

if ! (get_ack "Do you want to continue?" N;) then
	echo "Exiting, bye!";
	exit 0;
fi

restart_service=false;

echo "Moving script files";
if test -f "./mdcsmarthub_telegram.py"; then
  sudo /bin/chown -R root:root ./mdcsmarthub_telegram.py
  sudo /bin/mkdir -p /etc/mdc/
  sudo /bin/mv ./mdcsmarthub_telegram.py /etc/mdc/
  restart_service=true;
else
  echo "Script files not present, skip";
fi

echo "Creating log folder for mdc";
if test -d "/var/log/mdc/"; then
  echo "Log folder already present, skip";
else
  sudo /bin/mkdir -p /var/log/mdc/
  restart_service=true;
fi

echo "Moving logrotate files";
if test -f "./mdcsmarthub_telegram.logrotate"; then
  sudo /bin/chown -R root:root ./mdcsmarthub_telegram.logrotate
  sudo /bin/mv ./mdcsmarthub_telegram.logrotate /etc/logrotate.d/mdcsmarthub_telegram
else
  echo "Logrotate files not present, skip";
fi

echo "Moving environment files";
if test -f "./mdcsmarthub_telegram.env"; then
  sudo /bin/chown -R root:root ./mdcsmarthub_telegram.env
  sudo /bin/mv ./mdcsmarthub_telegram.env /etc/default/mdcsmarthub_telegram
  restart_service=true;
else
  echo "Environment files not present, skip";
fi

echo "Moving service files";
if test -f "./mdcsmarthub_telegram.service"; then
  sudo /bin/chown -R root:root ./mdcsmarthub_telegram.service
  sudo /bin/mv ./mdcsmarthub_telegram.service /lib/systemd/system/mdcsmarthub_telegram.service
  restart_service=true;
else
  echo "Service files not present, skip";
fi

echo "Reload and reboot service";
if $restart_service; then
  sudo /bin/systemctl daemon-reload
  sudo /bin/systemctl enable mdcsmarthub_telegram.service
  sudo /bin/systemctl restart mdcsmarthub_telegram.service
else
  echo "No changes to service related files, skip";
fi

echo "Done";
