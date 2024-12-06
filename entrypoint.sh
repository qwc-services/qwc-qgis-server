#!/bin/bash

# Generate any requested non-en_US locale
if [ $LOCALE != 'en_US' ]; then
  echo "Compiling locale definition for $LOCALE"
  # NOTE: Write to /tmp/locale-archive to allow unprivileged users to create locales
  mkdir -p /tmp/locale-archive
  localedef -i $LOCALE -c -f UTF-8 -A /usr/share/locale/locale.alias /tmp/locale-archive/$LOCALE.UTF-8
  export LOCPATH=/tmp/locale-archive
  export LANG=${LOCALE}.UTF-8
  export LC_ALL=${LOCALE}.UTF-8
fi

echo Updating fonts...
fc-cache -f && fc-list | sort

# Copy for processing
cp /etc/apache2/templates/qgis-server.conf.template /tmp/qgis-server.conf.template

# Substitute arbitrary extra ENVs
ORIG_IFS=$IFS
IFS=","
for extra_env in $FCGID_EXTRA_ENV; do
  if [ ! -z ${!extra_env} ]; then
    sed -i "s|@FCGID_EXTRA_ENV@|FcgidInitialEnv ${extra_env} ${!extra_env}\n@FCGID_EXTRA_ENV@|" /tmp/qgis-server.conf.template
  fi
done
IFS=$ORIG_IFS
sed -i "s|@FCGID_EXTRA_ENV@||" /tmp/qgis-server.conf.template

# Substitute predefined variables from ENV
envsubst < /tmp/qgis-server.conf.template > /etc/apache2/sites-enabled/qgis-server.conf

rm /tmp/qgis-server.conf.template

# Replace Port
sed -i -e "s/Listen 80/Listen $PORT/" /etc/apache2/ports.conf

# Activate the Ubuntu Apache environment
. /etc/apache2/envvars

> $QGIS_SERVER_LOG_FILE
tail -f $QGIS_SERVER_LOG_FILE > /proc/self/fd/2 &
exec /usr/sbin/apache2 -k start -DFOREGROUND &>> $QGIS_SERVER_LOG_FILE
