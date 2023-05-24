#!/bin/sh

echo Updating fonts...
fc-cache -f && fc-list | sort

# Substitute variables from ENV
envsubst < /etc/apache2/templates/qgis-server.conf.template > /etc/apache2/sites-enabled/qgis-server.conf

# Activate the Ubuntu Apache environment
. /etc/apache2/envvars

exec /usr/sbin/apache2 -k start -DFOREGROUND
