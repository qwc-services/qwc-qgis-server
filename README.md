[![CI](https://github.com/qwc-services/qwc-qgis-server/actions/workflows/qgis-server.yml/badge.svg)](https://github.com/qwc-services/qwc-qgis-server/actions)
[![docker](https://img.shields.io/docker/v/sourcepole/qwc-qgis-server?label=qwc-qgis-server%20image&sort=semver)](https://hub.docker.com/r/sourcepole/qwc-qgis-server)


QWC QGIS Server
===============

QGIS server Docker image for QWC.


Configuring a proxy server
--------------------------

Mount a file with contents
```
[proxy]
proxyEnabled=true
proxyType=HttpProxy
proxyHost=myproxyhost
proxyPort=8080
```
to `/etc/QGIS/QGIS3.ini`.


Loading QGIS projects from database
-----------------------------------

QGIS Server can load QGIS projects directly from a postgresql database.

This image is preconfigured to load projects from the database when QGIS Server is called as follows:

    http://localhost:8001/qgis/pg:<schema>.<projectname>

It will use the `qgisprojects` postgresql service connection, which must be defined in the `pg_service.conf` which is mounted into the `qwc-qgis-server` container.
