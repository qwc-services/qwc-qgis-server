# QGIS Server 3 with Apache FCGI

FROM phusion/baseimage:jammy-1.0.1

MAINTAINER Pirmin Kalberer

# Add de_DE.UTF-8 and fr_FR.UTF-8 to locales
RUN locale-gen de_DE.UTF-8 fr_FR.UTF-8 && update-locale
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ARG QGIS_REPO=ubuntu

# Install dependencies:
# - Fonts
# - Headless X Server
# - Apache + FCGI
# - QGIS Server
RUN \
    apt-get update && \
    apt-get install -y fontconfig fonts-dejavu ttf-bitstream-vera fonts-liberation fonts-ubuntu && \
    apt-get install -y xvfb && \
    apt-get install -y apache2 libapache2-mod-fcgid && \
    curl -L https://qgis.org/downloads/qgis-2022.gpg.key | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import && \
    chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg && \
    echo "deb https://qgis.org/$QGIS_REPO jammy main" > /etc/apt/sources.list.d/qgis.org.list && \
    apt-get update && \
    apt-get install -y qgis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add additional user fonts
ADD fonts/* /usr/share/fonts/truetype/
RUN fc-cache -f && fc-list | sort

# Configure xvfb
RUN mkdir /etc/service/xvfb
ADD xvfb-run.sh /etc/service/xvfb/run
RUN chmod +x /etc/service/xvfb/run

# Configure apache
#RUN a2dismod mpm_event
#RUN a2enmod mpm_worker
RUN a2enmod rewrite
RUN a2enmod fcgid
RUN a2enmod headers

# Writeable dir for qgis_mapserv.log and qgis-auth.db
RUN mkdir /var/log/qgis && chown www-data:www-data /var/log/qgis
RUN mkdir /var/lib/qgis && chown www-data:www-data /var/lib/qgis
ARG URL_PREFIX=/qgis
ARG QGIS_SERVER_LOG_LEVEL=1
ADD qgis3-server.conf /etc/apache2/sites-enabled/qgis-server.conf
RUN sed -i "s!@URL_PREFIX@!$URL_PREFIX!g; s!@QGIS_SERVER_LOG_LEVEL@!$QGIS_SERVER_LOG_LEVEL!g" /etc/apache2/sites-enabled/qgis-server.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf

RUN mkdir /etc/service/apache2
ADD apache2-run.sh /etc/service/apache2/run
RUN chmod +x /etc/service/apache2/run

RUN mkdir /etc/service/dockerlog
ADD dockerlog-run.sh /etc/service/dockerlog/run
RUN chmod +x /etc/service/dockerlog/run

EXPOSE 80

VOLUME ["/data"]

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]
