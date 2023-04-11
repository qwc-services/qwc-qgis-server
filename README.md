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
