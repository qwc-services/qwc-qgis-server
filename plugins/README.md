QWC QGIS Server plugins
=======================

Plugins for extending QGIS Server for QWC.

# datasource_filter_username

This plugin will replace `$QWC_USERNAME$` in datasource filter expressions with the current QWC username, passed via `QWC_USERNAME` query parameter to the QGIS Server. The `QWC_USERNAME` parameter is passed by default by the `qwc-ogc-service`, `qwc-feature-info-service` and `qwc-legend-service`. Furthermore, `$QWC_USERNAME$` in a datasource filter expression will also be replaced by the `qwc-data-service` in the queries it builds. Useful limit a dataset to a subset based on the logged in user.

# filter_geom

This plugin implements `FILTER_GEOM` for WMS GetMap and GetLegendGraphics. It works by injecting a corresponding `FILTER` expression for each applicable layer. Currently, only postgis layers will be filtered.

# get_translations

This plugin returns project translations (i.e. layer and field names) read from the `<projectname>_<lang>.ts` translations, also used in QGIS Desktop, plus auxiliary translations from a `<projectname>_<lang>.json` for translations which are not (yet) handled by the QGIS project translation mechanism.

See [translated themes documentation](https://qwc-services.github.io/master/topics/Translations/#translated-themes).

# print_templates

This plugin allows managing print templates as `.qpt` files in a specified `PRINT_LAYOUT_DIR`, which are then made available to all projects in `GetPrint` requests.

See [print templates documentation](https://qwc-services.github.io/master/topics/Printing/#layout-templates).

# split_categorized

This plugin will expose categorized layer symbologies as separate layers.

See [categorized layers documentation](https://qwc-services.github.io/master/configuration/ThemesConfiguration/#split-categorized-layers).

# wms_geotiff_output

This plugin adds support for geotiff output to WMS GetMap.

# clear_capabilities

Clears the WMS cache before GetCapabilities or GetProjectSettings requests.
