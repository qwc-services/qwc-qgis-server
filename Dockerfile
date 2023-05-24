# QGIS Server 3 with Apache FCGI

FROM ubuntu:jammy

ARG QGIS_REPO=ubuntu

# Install dependencies:
# - Locales
# - Fonts
# - Apache + FCGI
# - QGIS Server
# - envsubst (gettext-base)
ENV DEBIAN_FRONTEND=noninteractive
RUN \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y locales && \
    apt-get install -y fontconfig fonts-dejavu ttf-bitstream-vera fonts-liberation fonts-ubuntu && \
    apt-get install -y apache2 libapache2-mod-fcgid && \
    apt-get install -y curl gpg gettext-base && \
    curl -L https://qgis.org/downloads/qgis-2022.gpg.key | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import && \
    chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg && \
    echo "deb https://qgis.org/$QGIS_REPO jammy main" > /etc/apt/sources.list.d/qgis.org.list && \
    apt-get update && \
    apt-get install -y qgis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add de_DE.UTF-8 and fr_FR.UTF-8 to locales
RUN locale-gen en_US.UTF-8 de_DE.UTF-8 fr_FR.UTF-8 && update-locale
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Configure apache
RUN a2enmod rewrite && a2enmod fcgid && a2enmod headers && \
    # Make sure apache2 logs to /dev/stdout and /dev/stderr
    # so we can see the logs with "docker logs"
    # See: https://github.com/docker-library/httpd/blob/b13054c7de5c74bbaa6d595dbe38969e6d4f860c/2.2/Dockerfile#L72-L75
    sed -ri \
		-e 's!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g' \
		-e 's!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g' \
		"/etc/apache2/apache2.conf"

# Writeable dir for qgis_mapserv.log and qgis-auth.db
RUN mkdir /var/lib/qgis && chown www-data:www-data /var/lib/qgis && \
    # Dir for QGIS.ini
    mkdir /etc/QGIS/ && \
    # Delete apache2 default site
    rm /etc/apache2/sites-enabled/000-default.conf

# ENV variables that will be used to configure QGIS server FCGI
# apache2 specific variables
ENV APACHE_LOG_LEVEL=info
ENV FCGI_IO_TIMEOUT=120
ENV FCGI_MIN_PROCESSES=3
ENV FCGI_MAX_PROCESSES=100
# QWC2 specific variables
ENV URL_PREFIX=/ows
# QGIS Server specific variables
ENV MAX_CACHE_LAYERS=500
ENV DB_PROJECT_SERVICE=qgisprojects
ENV QGIS_DEBUG=1
ENV QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS=""
ENV QGIS_SERVER_API_WFS3_MAX_LIMIT=10000
ENV QGIS_SERVER_CACHE_SIZE=268435456
ENV QGIS_SERVER_DISABLE_GETPRINT=false
ENV QGIS_SERVER_FORCE_READONLY_LAYERS=false
ENV QGIS_SERVER_IGNORE_BAD_LAYERS=false
ENV QGIS_SERVER_LANDING_PAGE_PREFIX=""
ENV QGIS_SERVER_LANDING_PAGE_PROJECTS_DIRECTORIES=""
ENV QGIS_SERVER_LANDING_PAGE_PROJECTS_PG_CONNECTIONS=""
ENV QGIS_SERVER_LOG_LEVEL=1
ENV QGIS_SERVER_LOG_PROFILE=false
ENV QGIS_SERVER_MAX_THREADS=-1
ENV QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE=""
ENV QGIS_SERVER_PARALLEL_RENDERING=false
ENV QGIS_SERVER_PROJECT_CACHE_CHECK_INTERVAL=0
ENV QGIS_SERVER_PROJECT_CACHE_STRATEGY=filesystem
ENV QGIS_SERVER_SERVICE_URL=""
ENV QGIS_SERVER_SHOW_GROUP_SEPARATOR=false
ENV QGIS_SERVER_TRUST_LAYER_METADATA=1
ENV QGIS_SERVER_WCS_SERVICE_URL=""
ENV QGIS_SERVER_WFS_SERVICE_URL=""
ENV QGIS_SERVER_WMS_MAX_HEIGHT=-1
ENV QGIS_SERVER_WMS_MAX_WIDTH=-1
ENV QGIS_SERVER_WMS_SERVICE_URL=""
ENV QGIS_SERVER_WMTS_SERVICE_URL=""
# Add apache config for QGIS server
ADD qgis3-server.conf.template /etc/apache2/templates/qgis-server.conf.template

# Add entrypoint
COPY entrypoint.sh /entrypoint.sh

EXPOSE 80

VOLUME ["/data"]

ENTRYPOINT ["/entrypoint.sh"]
