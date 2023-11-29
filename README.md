[![CI](https://github.com/qwc-services/qwc-qgis-server/actions/workflows/qgis-server.yml/badge.svg)](https://github.com/qwc-services/qwc-qgis-server/actions)
[![docker](https://img.shields.io/docker/v/sourcepole/qwc-qgis-server?label=qwc-qgis-server%20image&sort=semver)](https://hub.docker.com/r/sourcepole/qwc-qgis-server)


QWC QGIS Server
===============

QGIS server Docker image for QWC.

Requests to `/ows/<project>` are mapped to `/data/<project>.qgs`.


Configuring FCGI with ENVs
--------------------------

The FCGI configuration of the QGIS Server can be configured by setting some environment variables.

Here is a list of all environment variables that can be currently set and their default values.
The list also contains information about which application the environment variables configure.

See [QGIS Server documentation](https://docs.qgis.org/3.28/en/docs/server_manual/config.html#environment-variables)
for more information about QGIS Server specifc environment variables.

| Name | Default | Application|
|------|---------|-------------
|URL_PREFIX|/ows|QWC2 Services|
|PORT|80|QGIS Server apache2 FCGI|
|APACHE_LOG_LEVEL|info|QGIS Server apache2 FCGI|
|FCGI_IO_TIMEOUT|120|QGIS Server apache2 FCGI|
|FCGI_MIN_PROCESSES|3 |QGIS Server apache2 FCGI|
|FCGI_MAX_PROCESSES|100|QGIS Server apache2 FCGI|
|FCGI_PROCESS_LIFE_TIME|3600|QGIS Server apache2 FCGI|
|FCGI_IDLE_TIMEOUT|300|QGIS Server apache2 FCGI|
|FCGI_MAX_REQUESTLEN|26214400|QGIS Server apache2 FCGI|
|FCGI_CONNECT_TIMEOUT|60|QGIS Server apache2 FCGI|
|MAX_CACHE_LAYERS|500|QGIS Server|
|QGIS_PROJECT_SUFFIX|qgs|QGIS Server|
|DB_PROJECT_SERVICE|qgisprojects|QGIS Server|
|QGIS_DEBUG|1 | QGIS Server|
|QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS|""|QGIS Server|
|QGIS_SERVER_API_WFS3_MAX_LIMIT|10000|QGIS Server|
|QGIS_SERVER_CACHE_SIZE|268435456|QGIS Server|
|QGIS_SERVER_DISABLE_GETPRINT|false|QGIS Server|
|QGIS_SERVER_FORCE_READONLY_LAYERS|false|QGIS Server|
|QGIS_SERVER_IGNORE_BAD_LAYERS|false|QGIS Server|
|QGIS_SERVER_LANDING_PAGE_PREFIX|""|QGIS Server|
|QGIS_SERVER_LANDING_PAGE_PROJECTS_DIRECTORIES|""|QGIS Server|
|QGIS_SERVER_LANDING_PAGE_PROJECTS_PG_CONNECTIONS|""|QGIS Server|
|QGIS_SERVER_LOG_LEVEL|1 |QGIS Server|
|QGIS_SERVER_LOG_PROFILE|false|QGIS Server|
|QGIS_SERVER_MAX_THREADS|-1|QGIS Server|
|QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE|""|QGIS Server|
|QGIS_SERVER_PARALLEL_RENDERING|false|QGIS Server|
|QGIS_SERVER_PROJECT_CACHE_CHECK_INTERVAL|0 |QGIS Server|
|QGIS_SERVER_PROJECT_CACHE_STRATEGY|filesystem|QGIS Server|
|QGIS_SERVER_SERVICE_URL|""|QGIS Server|
|QGIS_SERVER_SHOW_GROUP_SEPARATOR|false|QGIS Server|
|QGIS_SERVER_TRUST_LAYER_METADATA|1 |QGIS Server|
|QGIS_SERVER_WCS_SERVICE_URL|""|QGIS Server|
|QGIS_SERVER_WFS_SERVICE_URL|""|QGIS Server|
|QGIS_SERVER_WMS_MAX_HEIGHT|-1|QGIS Server|
|QGIS_SERVER_WMS_MAX_WIDTH|-1|QGIS Server|
|QGIS_SERVER_WMS_SERVICE_URL|""|QGIS Server|
|QGIS_SERVER_WMTS_SERVICE_URL|""|QGIS Server|

Other QGIS Server settings that are used:

* QGIS_CUSTOM_CONFIG_PATH: "/var/lib/qgis"
* QGIS_AUTH_DB_DIR_PATH: "/var/lib/qgis"
* QGIS_OPTIONS_PATH: "/etc"
* QGIS_PLUGINPATH: "/usr/share/qgis/python/plugins"
* QGIS_SERVER_API_RESOURCES_DIRECTORY: "/usr/share/qgis/resources/server/api"
* QGIS_SERVER_CACHE_DIRECTORY: "/.cache"
* PGSERVICEFILE: "/etc/postgresql-common/pg_service.conf"


Additional ENV-vars
-------------------

You can pass arbitrary environment variables to FCGI by setting `FCGID_EXTRA_ENV` to a comma-separated list of additional variables,
and then setting the variables itself. This is useful for instance for qgis server plugins.

Example:

      FCGID_EXTRA_ENV=FOO,BAR
      FOO=foo_val
      BAR=bar_val


Additional fonts
----------------

To add additional fonts, mount your font directoy to `/usr/local/share/fonts`.

Locale
------

The default locale is `en_US`. You can choose a different locale by setting the `LOCALE` environment variable to `lang_COUNTRY` (i.e. `de_CH`).

Additional datum grids
----------------------

Some projections may need additional datum grids for best accuracy. These are available at [https://cdn.proj.org/](https://cdn.proj.org/). Please mount these files below `/usr/share/proj`.

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

    http://localhost:8001/qgis/pg/<schema>/<projectname>

It will use the `qgisprojects` postgresql service connection, which must be defined in the `pg_service.conf` which is mounted into the `qwc-qgis-server` container.
