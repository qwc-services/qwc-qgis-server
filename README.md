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

See [QGIS Server documentation](https://docs.qgis.org/latest/en/docs/server_manual/config.html#environment-variables)
for more information about QGIS Server specifc environment variables.

| Name                                   | Default      |
|----------------------------------------|--------------|
|`URL_PREFIX`                            |`/ows`        |
|`ENABLED_PLUGINS`                       |`[]`          |
|`PORT`                                  |`80`          |
|`APACHE_LOG_LEVEL`                      |`info`        |
|`FCGI_IO_TIMEOUT`                       |`120`         |
|`FCGI_MIN_PROCESSES`                    |`3`           |
|`FCGI_MAX_PROCESSES`                    |`100`         |
|`FCGI_PROCESS_LIFE_TIME`                |`3600 `       |
|`FCGI_IDLE_TIMEOUT`                     |`300`         |
|`FCGI_MAX_REQUESTLEN`                   |`26214400`    |
|`FCGI_CONNECT_TIMEOUT`                  |`60`          |
|`MAX_CACHE_LAYERS`                      |`500`         |
|`QGIS_PROJECT_SUFFIX`                   |`qgs`         |
|`DB_PROJECT_SERVICE`                    |`qgisprojects`|
|`QGIS_DEBUG`                            |`0`           |
|`QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS`  |`""`          |
|`QGIS_SERVER_API_WFS3_MAX_LIMIT`        |`10000`       |
|`QGIS_SERVER_CACHE_SIZE`                |`52428800`    |
|`QGIS_SERVER_CAPABILITIES_CACHE_SIZE`   |`40`          |
|`QGIS_SERVER_DISABLE_GETPRINT`          |`false`       |
|`QGIS_SERVER_FORCE_READONLY_LAYERS`     |`false`       |
|`QGIS_SERVER_IGNORE_BAD_LAYERS`         |`false`       |
|`QGIS_SERVER_LANDING_PAGE_PREFIX`       |`""`          |
|`QGIS_SERVER_LANDING_PAGE_PROJECTS_DIRECTORIES` |`""`  |
|`QGIS_SERVER_LANDING_PAGE_PROJECTS_PG_CONNECTIONS`|`""`|
|`QGIS_SERVER_LOG_LEVEL`                 |`1`           |
|`QGIS_SERVER_LOG_PROFILE`               |`false`       |
|`QGIS_SERVER_MAX_THREADS`               |`-1`          |
|`QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE`    |`""`          |
|`QGIS_SERVER_PARALLEL_RENDERING`        |`false`       |
|`QGIS_SERVER_PROJECT_CACHE_CHECK_INTERVAL`|`0`         |
|`QGIS_SERVER_PROJECT_CACHE_STRATEGY`    |`filesystem`  |
|`QGIS_SERVER_PROJECT_CACHE_SIZE`        |`100`         |
|`QGIS_SERVER_SERVICE_URL`               |`""`          |
|`QGIS_SERVER_SHOW_GROUP_SEPARATOR`      |`false`       |
|`QGIS_SERVER_TRUST_LAYER_METADATA`      |`1`           |
|`QGIS_SERVER_WCS_SERVICE_URL`           |`""`          |
|`QGIS_SERVER_WFS_SERVICE_URL`           |`""`          |
|`QGIS_SERVER_WMS_MAX_HEIGHT`            |`-1`          |
|`QGIS_SERVER_WMS_MAX_WIDTH`             |`-1`          |
|`QGIS_SERVER_WMS_SERVICE_URL`           |`""`          |
|`QGIS_SERVER_WMTS_SERVICE_URL`          |`""`          |

Other QGIS Server environment variables that set (harcoded):

| Name                                | Value                                  |
|-------------------------------------|----------------------------------------|
|`QGIS_CUSTOM_CONFIG_PATH`            |`/var/lib/qgis`                         |
|`QGIS_AUTH_DB_DIR_PATH`              |`/var/lib/qgis`                         |
|`QGIS_OPTIONS_PATH`                  |`/etc`                                  |
|`QGIS_PLUGINPATH`                    |`/usr/share/qgis/python/plugins`        |
|`QGIS_SERVER_API_RESOURCES_DIRECTORY`|`/usr/share/qgis/resources/server/api`  |
|`QGIS_SERVER_CACHE_DIRECTORY`        |`/.cache`                               |
|`PGSERVICEFILE`                      |`/etc/postgresql-common/pg_service.conf`|


Additional ENV-vars
-------------------

You can pass arbitrary environment variables to FCGI by setting `FCGID_EXTRA_ENV` to a comma-separated list of additional variables,
and then setting the variables itself. This is useful for instance for qgis server plugins. This variables will be used at FCGI initialization time.

Example:

      FCGID_EXTRA_ENV=FOO,BAR
      FOO=foo_val
      BAR=bar_val

You can also pass arbitrary environment variables to FCGI by setting `PASS_EXTRA_ENV` to a comma-separated list of additional variables,
and then setting the variables itself. This is useful when running providers with runtime loading environnment (as GDAL driver 'Microsoft Azure blob containers').

Example:

      PASS_EXTRA_ENV=FOO,BAR
      FOO=foo_val
      BAR=bar_val


Plugins
-------

The `qwc-qgis-server` image includes a set of [plugins](plugins) which are required for various QWC functionalities.

These plugins are disabled by default and must be enabled listing the respective plugin names in the `ENABLED_PLUGINS` Env-Var, i.e.
```
ENABLED_PLUGINS: '["print_templates", "get_translations"]'
```

The available plugins are as follows:

| Plugin name                 | Description |
|-----------------------------|-------------|
|`datasource_filter_username` | Replacees `$QWC_USERNAME$` in datasource filter expressions with the current QWC username, passed via `QWC_USERNAME` query parameter to the QGIS Server. The `QWC_USERNAME` parameter is passed by default by the `qwc-ogc-service`. Furthermore, `$QWC_USERNAME$` in a datasource filter expression will also be replaced by the `qwc-data-service` in the queries it builds. Useful limit a dataset to a subset based on the logged in user. |
|`filter_geom`                | Implements `FILTER_GEOM` for WMS GetMap and GetLegendGraphics. It works by injecting a corresponding `FILTER` expression for each applicable layer. Currently, only postgis layers will be filtered. |
|`get_translations`           | Returns project translations (i.e. layer and field names) read from the `<projectname>_<lang>.ts` translations, also used in QGIS Desktop, plus auxiliary translations from a `<projectname>_<lang>.json` for translations which are not (yet) handled by the QGIS project translation mechanism. See [translated themes documentation](https://qwc-services.github.io/master/topics/Translations/#translated-themes). |
|`print_templates`            | Allows managing print templates as `.qpt` files in a specified `PRINT_LAYOUT_DIR`, which are then made available to all projects in `GetPrint` requests. See [print templates documentation](https://qwc-services.github.io/master/topics/Printing/#layout-templates). |
|`split_categorized`          | Expose categorized layer symbologies as separate layers. See [categorized layers documentation](https://qwc-services.github.io/master/configuration/ThemesConfiguration/#split-categorized-layers). |
|`wms_geotiff_output`         | Adds support for GEOTIFF output to WMS GetMap. |
|`clear_capabilities`         | Clears the WMS cache before GetCapabilities or GetProjectSettings requests. |

You can also add custom plugins by mounting these to the `plugins` folder inside the container:
```yml
  qwc-qgis-server:
    image: docker.io/sourcepole/qwc-qgis-server:<TAG>
  ...
  volumes:
   - ./volumes/qwc-qgis-server-plugins/<plugin_name>:/usr/share/qgis/python/plugins/<plugin_name>:ro
```

Additional fonts
----------------

To add additional fonts, mount your font directoy to `/usr/local/share/fonts`.

Locale
------

The default locale is `en_US`. You can choose a different locale by setting the `LOCALE` environment variable to `lang_COUNTRY` (i.e. `de_CH`).

Additional datum grids
----------------------

Some projections may need additional datum grids for best accuracy. These are available at [https://cdn.proj.org/](https://cdn.proj.org/). Please mount these files below `/usr/share/proj`.

Setting QGIS settings
---------------------

To change QGIS settings, mount a `QGIS3.ini` file to `/etc/QGIS/QGIS3.ini` with the desired configuration.

For instance, you can configure a proxy server or modify the network timeout:
```
[proxy]
proxyEnabled=true
proxyType=HttpProxy
proxyHost=myproxyhost
proxyPort=8080

[network]
network-timeout=10000
```

Loading QGIS projects from database
-----------------------------------

QGIS Server can load QGIS projects directly from a postgresql database.

This image is preconfigured to load projects from the database when QGIS Server is called as follows:

    http://localhost:8001/ows/pg/<schema>/<projectname>

It will use the `qgisprojects` postgresql service connection, which must be defined in the `pg_service.conf` which is mounted into the `qwc-qgis-server` container.

Log monitoring
--------------

You can monitor the `n` last lines of the QGIS Server logs via `/logs?n=<n>`, i.e. `http://localhost:8001/logs?n=100`.

Debugging
---------

The basic QGIS Server log output verbosity can be controlled via `QGIS_SERVER_LOG_LEVEL` (see https://docs.qgis.org/3.40/en/docs/server_manual/config.html). A `QGIS_SERVER_LOG_LEVEL: 0` will enable the most verbose log output. Default ist `QGIS_SERVER_LOG_LEVEL: 1`.

For further debugging, nightly release debug images are available, which are tagged as `<version>-nightly>`. You can enable debug output by setting `QGIS_DEBUG` to a level above 0 (the higher the level, the more verbose the log output). Sample `docker-compose.yml` configuration:

```yml
  qwc-qgis-server:
    image: docker.io/sourcepole/qwc-qgis-server:3.44-nightly
    environment:
      QGIS_SERVER_LOG_LEVEL: 0
      QGIS_DEBUG: 1
    ...
```

For even further debugging, you can locally build the `qwc-qgis-server` image with root access as follows:

```yml
  qwc-qgis-server:
    build:
      context: ./qwc-services/qwc-qgis-server
      args:
        QGIS_REPO: <ubuntu|ubuntu-ltr|ubuntu-nightly-release>
        ROOT_PASSWORD: '<password>'
    ...
```

and then install the debug tools of your choice inside the container (`docker compose exec qwc-qgis-server bash`).
