#
# Copyright (c) 2024 Marco Hugentobler, Sourcepole AG
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

from qgis.core import Qgis, QgsMessageLog, QgsProject
from qgis.server import QgsServerFilter, QgsConfigCache, QgsServerSettings
from qgis.PyQt.QtCore import QFileInfo
import shutil
import os


class ClearCapabilitiesFilter(QgsServerFilter):
    """ QGIS Server ClearCapabilitiesFilter plugin. """

    def __init__(self, server_iface):
        super(ClearCapabilitiesFilter, self).__init__(server_iface)
        self.projects = {}

    def requestReady(self):
        handler = self.serverInterface().requestHandler()
        params = handler.parameterMap()
        if params.get("CLEARCACHE") and params.get("MAP", ""):
            self.clearWmsCache()
            self.clearCache(params.get("MAP", ""))
        elif (params.get("SERVICE", "").upper() in ["WMS", "WMTS", "WFS"]
                and params.get("REQUEST", "").upper() in [
                    "GETPROJECTSETTINGS", "GETCAPABILITIES"]
                and params.get("MAP", "")):
            self.clearCacheIfModified(params.get("MAP", ""))

    def clearCacheIfModified(self, project):
        """ Checks the project timestamps and clears cache on update """
        fi = QFileInfo(project)

        if fi.exists():
            lm = fi.lastModified()

            if self.projects.get(project, lm) < lm:
                self.clearCache(project)
                QgsMessageLog.logMessage(
                    "Cached cleared after update: {} [{}]".format(
                        project, lm.toString()),
                    "ClearCapabilities", Qgis.Warning)

            self.projects[project] = lm

    def clearWmsCache(self):
        settings = QgsServerSettings()
        settings.load()
        shutil.rmtree(os.path.join(settings.cacheDirectory(), 'data8'),
                      ignore_errors=True)
        # QgsProject.instance().removeAllMapLayers()

    def clearCache(self, project):
        # QgsConfigCache.instance().removeEntry(project)
        # cache = QgsCapabilitiesCache()
        # cache.removeCapabilitiesDocument(project)
        self.serverInterface().removeConfigCacheEntry(project)

        QgsMessageLog.logMessage(
            "Cached cleared : {}".format(project),
            "ClearCapabilities", Qgis.Warning)


class ClearCapabilities:
    """ Clear Capabilities plugin: this gets loaded by the server at
        start and creates the CLEARCACHE request.
    """

    def __init__(self, server_iface):
        """Register the filter"""
        clear_capabilities = ClearCapabilitiesFilter(server_iface)
        server_iface.registerFilter(clear_capabilities)
