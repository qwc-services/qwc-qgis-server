# QGIS Server 3 with Apache FCGI

FROM ubuntu:jammy

MAINTAINER Pirmin Kalberer

ARG QGIS_REPO=ubuntu
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies:
# - Locales
# - Fonts
# - Apache + FCGI
# - QGIS Server
# - envsubst (gettext-base)
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

# Add additional user fonts
ADD fonts/* /usr/share/fonts/truetype/

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
RUN mkdir /var/lib/qgis && chown www-data:www-data /var/lib/qgis
# Dir for QGIS.ini
RUN mkdir /etc/QGIS/
# ENV variables that will be used to configure FCGI env variables
ENV URL_PREFIX=/ows
ENV QGIS_SERVER_LOG_STDERR=1
ENV QGIS_SERVER_LOG_LEVEL=1
ENV QGIS_SERVER_IGNORE_BAD_LAYERS=false
ENV QGIS_DEBUG=1
ENV MAX_CACHE_LAYERS=500
ENV QGIS_OPTIONS_PATH=/etc
ENV DB_PROJECT_SERVICE=qgisprojects
# Add apache config for QGIS server
ADD qgis3-server.conf.template /etc/apache2/templates/qgis-server.conf.template
RUN rm /etc/apache2/sites-enabled/000-default.conf

RUN mkdir /usr/local/bin/apache2
ADD --chmod=+x apache2-run.sh /usr/local/bin/apache2/run

EXPOSE 80

VOLUME ["/data"]

CMD ["/usr/local/bin/apache2/run"]
