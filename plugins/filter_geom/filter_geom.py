#
# Copyright (c) 2024 Sandro Mani, Sourcepole AG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from qgis.core import *
from qgis.server import *
from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import QDomDocument
import os

class FilterGeomFilter(QgsServerFilter):
    def __init__(self, serverIface):
        super(FilterGeomFilter, self).__init__(serverIface)
        self.__layouts = []
        self.__project = None
        
    def onRequestReady(self):
        
        # Only apply FILTER_GEOM to GetMap and GetLegendGraphics. GetFeatureInfo already honours it
        request = self.serverInterface().requestHandler()
        requestParam = request.parameter('REQUEST').upper()
        filterGeomParam = request.parameter('FILTER_GEOM')
        filterParam = request.parameter('FILTER')
        layersParam = request.parameter('LAYERS').split(",")
        crsParam = request.parameter('SRS')
        if not crsParam:
            crsParam = request.parameter('CRS')
        srid = crsParam[5:]
        if not requestParam in ['GETMAP', 'GETLEGENDGRAPHICS', 'GETPRINT'] or not filterGeomParam:
            return True

        # Inject st_intersects and st_geomfromtext tokens if necessary
        extraTokens = [token.lower() for token in filter(bool, os.getenv("QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS", "").split(","))]
        changed = False
        for token in ["st_intersects", "st_geomfromtext", "st_transform"]:
            if not token in extraTokens:
                extraTokens.append(token)
                changed = True
        if changed:
            os.environ["QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS"] = ",".join(extraTokens)
            self.serverInterface().reloadSettings()
            QgsMessageLog.logMessage(
                f"Altered QGIS_SERVER_ALLOWED_EXTRA_SQL_TOKENS to %s" % (",".join(extraTokens)), "FilterGeom", Qgis.MessageLevel.Info
            )

        projectPath = self.serverInterface().configFilePath()
        try:
            project = QgsConfigCache.instance().project(projectPath)
        except:
            return True
        filters = dict(map(lambda entry: entry.split(":"), filter(bool, filterParam.split(";"))))

        # Append geometry filter expression to all postgis layers
        for layer in project.mapLayers().values():

            layername = layer.shortName()
            if QgsServerProjectUtils.wmsUseLayerIds(project):
                layername = layer.id()
            elif not layername:
                layername = layer.name()

            if not layername in layersParam:
                continue

            filterExpr = None
            if layer.providerType() == "postgres":
                geomColumn = QgsDataSourceUri(layer.source()).geometryColumn()
                filterExpr = "ST_Intersects ( \"%s\" , ST_Transform ( ST_GeomFromText ( '%s' , %s ) , %d ) )" % (geomColumn, filterGeomParam, srid, layer.crs().postgisSrid())
            # elif layer.providerType() == "ogr" and layer.source().split("|")[0].lower().endswith(".gpkg"):
            #     tablename = layer.source().split('layername=')[-1]
            #     geomColumn = QgsMapLayerUtils.databaseConnection(layer).table('', tablename).geometryColumn()
            #     filterExpr = "ST_Intersects ( \"%s\" , ST_GeomFromText ( '%s' , %s ) )" % (geomColumn, filterGeomParam, srid)

            if filterExpr:
                if layername in filters:
                    filters[layername] += " AND " + filterExpr
                else:
                    filters[layername] = filterExpr

                # QgsMessageLog.logMessage(
                #     f"XXX New filter for %s = %s" % (layername, filters[layername]), "FilterGeom", Qgis.MessageLevel.Info
                # )

        newFilter = ";".join(map(lambda entry: ":".join(entry), filters.items()))
        request.setParameter('FILTER', newFilter)
        request.removeParameter('FILTER_GEOM')
        QgsMessageLog.logMessage(
            f"FILTER changed to %s" % newFilter, "FilterGeom", Qgis.MessageLevel.Info
        )

        if requestParam == 'GETPRINT':
            prefix = self.get_map_param_prefix(request.parameterMap())
            request.setParameter(prefix + ':FILTER', newFilter)
            request.removeParameter(prefix + ':FILTER_GEOM')

        return True

    def get_map_param_prefix(self, params):
        # Deduce map name by looking for param which ends with :EXTENT
        # (Can't look for param ending with :LAYERS as there might be i.e. A:LAYERS for the external layer definition A)
        mapname = ""
        for key, value in params.items():
            if key.endswith(":EXTENT"):
                return key[0:-7]
        return ""

class FilterGeom:
    def __init__(self, serverIface):
        self.iface = serverIface
        serverIface.registerFilter(FilterGeomFilter(serverIface))
