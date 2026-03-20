#!/bin/sh

### BEGIN INIT INFO
# Provides: Start SuperTwister python script
# Required-Start: existing python scripts in /usr/bin/local/
# Required-Stop: runnin twister script
# Should-Start:
# Should-Stop:
# Default-Start:S
# Default-Stop:
# Short-Description: .sh script to run SuperTwister after login
### END INIT INFO

PATH="/usr/local/bin/supertwister"
NAME="default.json"
DESC="SuperTwister Application manager"

#test -x "${PATH}/config.py" || exit 0

#if [ -r "${PATH}/${NAME}" ]
#then
#	. "${PATH}/${NAME}"
#fi
#set -e

cd "${PATH}"
/usr/bin/python3 main.py

exit 0
