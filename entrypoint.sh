#!/bin/sh

# Generate any requested non-en_US locale
if [ $LOCALE != 'en_US' ]; then
  echo "Compiling locale definition for $LOCALE"
  # NOTE: Write to /tmp/locale-archive to allow unprivileged users to create locales
  mkdir /tmp/locale-archive
  localedef -i $LOCALE -c -f UTF-8 -A /usr/share/locale/locale.alias /tmp/locale-archive/$LOCALE.UTF-8
  export LOCPATH=/tmp/locale-archive
  export LANG=${LOCALE}.UTF-8
fi

echo Updating fonts...
fc-cache -f && fc-list | sort

# Substitute variables from ENV
envsubst < /etc/apache2/templates/qgis-server.conf.template > /etc/apache2/sites-enabled/qgis-server.conf

# Replace Port
sed -i -e "s/Listen 80/Listen $PORT/" /etc/apache2/ports.conf

# Activate the Ubuntu Apache environment
. /etc/apache2/envvars

exec /usr/sbin/apache2 -k start -DFOREGROUND
