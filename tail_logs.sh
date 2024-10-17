#!/bin/bash

# Content-type header for proper HTTP response
echo "Content-type: text/plain; charset=utf-8"
echo ""

DEFAULT_LINES=100

LOG_FILE="$(grep QGIS_SERVER_LOG_FILE /etc/apache2/sites-enabled/qgis-server.conf | awk '{print $3}')"

# Get query string and extract the 'n' parameter if provided
QUERY_STRING="$QUERY_STRING"
LINES=$(echo "$QUERY_STRING" | grep -oP '(?<=n=)\d+')

if [ -z "$LINES" ]; then
  LINES=$DEFAULT_LINES
fi

if [ ! -f "$LOG_FILE" ]; then
  echo "Log file not found!"
  exit 1
fi

tail -n $LINES "$LOG_FILE"
