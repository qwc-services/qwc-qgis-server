# QGIS Server 3 with Apache FCGI

FROM ubuntu:noble

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
    curl -o /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg && \
    echo "\
Types: deb deb-src\n\
URIs: https://qgis.org/$QGIS_REPO\n\
Suites: noble\n\
Architectures: amd64\n\
Components: main\n\
Signed-By: /etc/apt/keyrings/qgis-archive-keyring.gpg\n\
" > /etc/apt/sources.list.d/qgis.sources && \
    apt-get update && \
    apt-get install -y qgis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8 && update-locale
ENV LOCALE en_US

# Configure apache
RUN a2enmod rewrite && a2enmod cgi && a2enmod fcgid && a2enmod headers && \
    # Make sure apache2 logs to /dev/stdout and /dev/stderr
    # so we can see the logs with "docker logs"
    # See: https://github.com/docker-library/httpd/blob/b13054c7de5c74bbaa6d595dbe38969e6d4f860c/2.2/Dockerfile#L72-L75
    sed -ri \
		-e 's!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g' \
		/etc/apache2/apache2.conf && \
    sed -ri \
        -e 's!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g' \
        /etc/apache2/conf-available/other-vhosts-access-log.conf && \
    # Delete apache2 default site
    rm /etc/apache2/sites-enabled/000-default.conf

ARG UID=33

RUN id $UID 2>/dev/null || useradd --system --uid $UID --create-home appuser

RUN \
    # Writeable dir for qgis-auth.db
    mkdir /var/lib/qgis && chown $UID /var/lib/qgis && \
    # Dir for QGIS.ini
    mkdir /etc/QGIS/ && \
    # Server cache directory ($QGIS_SERVER_CACHE_DIRECTORY)
    mkdir /.cache && chown $UID /.cache && \
    # Profile cache directory ($QGIS_OPTIONS_PATH/cache), i.e. for wfs provider cache
    mkdir /etc/cache && chown $UID /etc/cache && \
    # Set write permissions for runtime usage
    chown $UID /var/www && \
    chown $UID /var/run/apache2 && \
    chown $UID /var/lib/apache2/fcgid && \
    chmod go+rw /var/lib/apache2/fcgid/sock && \
    chown $UID /etc/apache2/sites-enabled && \
    chown $UID /etc/apache2/ports.conf && \
    chown $UID /etc/apache2

# ENV variables that will be used to configure QGIS server FCGI
# apache2 specific variables
ENV APACHE_LOG_LEVEL=info
ENV FCGI_IO_TIMEOUT=120
ENV FCGI_MIN_PROCESSES=3
ENV FCGI_MAX_PROCESSES=100
# Set to 0 to disable lifetime check
ENV FCGI_PROCESS_LIFE_TIME=3600
# Set to 0 to disable idle check
ENV FCGI_IDLE_TIMEOUT=300
ENV FCGI_MAX_REQUESTLEN=26214400
ENV FCGI_CONNECT_TIMEOUT=60
# QWC2 specific variables
ENV URL_PREFIX=/ows
ENV QGIS_PROJECT_SUFFIX=qgs
ENV DB_PROJECT_SERVICE=qgisprojects
# QGIS Server specific variables
ENV MAX_CACHE_LAYERS=500
ENV QGIS_DEBUG=1
ENV QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS=""
ENV QGIS_SERVER_API_WFS3_MAX_LIMIT=10000
ENV QGIS_SERVER_CACHE_SIZE=0
ENV QGIS_SERVER_CAPABILITIES_CACHE_SIZE=40
ENV QGIS_SERVER_DISABLE_GETPRINT=false
ENV QGIS_SERVER_FORCE_READONLY_LAYERS=false
ENV QGIS_SERVER_IGNORE_BAD_LAYERS=false
ENV QGIS_SERVER_LANDING_PAGE_PREFIX=""
ENV QGIS_SERVER_LANDING_PAGE_PROJECTS_DIRECTORIES=""
ENV QGIS_SERVER_LANDING_PAGE_PROJECTS_PG_CONNECTIONS=""
ENV QGIS_SERVER_LOG_LEVEL=1
ENV QGIS_SERVER_LOG_FILE="/tmp/qgis_server.log"
ENV QGIS_SERVER_LOG_PROFILE=false
ENV QGIS_SERVER_MAX_THREADS=-1
ENV QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE=""
ENV QGIS_SERVER_PARALLEL_RENDERING=false
ENV QGIS_SERVER_PROJECT_CACHE_CHECK_INTERVAL=0
ENV QGIS_SERVER_PROJECT_CACHE_STRATEGY=filesystem
ENV QGIS_SERVER_PROJECT_CACHE_SIZE=100
ENV QGIS_SERVER_SERVICE_URL=""
ENV QGIS_SERVER_SHOW_GROUP_SEPARATOR=false
ENV QGIS_SERVER_TRUST_LAYER_METADATA=1
ENV QGIS_SERVER_WCS_SERVICE_URL=""
ENV QGIS_SERVER_WFS_SERVICE_URL=""
ENV QGIS_SERVER_WMS_MAX_HEIGHT=-1
ENV QGIS_SERVER_WMS_MAX_WIDTH=-1
ENV QGIS_SERVER_WMS_SERVICE_URL=""
ENV QGIS_SERVER_WMTS_SERVICE_URL=""
ENV FCGID_EXTRA_ENV=""

# Add apache config for QGIS server
ADD qgis3-server.conf.template /etc/apache2/templates/qgis-server.conf.template

# Add tail_logs.sh script
ADD tail_logs.sh /usr/lib/cgi-bin/tail_logs.sh

# Add entrypoint
COPY entrypoint.sh /entrypoint.sh

USER $UID

ENV PORT=80
EXPOSE $PORT

VOLUME ["/data"]

ENTRYPOINT ["/entrypoint.sh"]
