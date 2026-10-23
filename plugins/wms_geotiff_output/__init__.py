#
# Copyright (c) 2023 Marco Hugentobler, Sourcepole AG
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

import json
import os


def serverClassFactory(serverIface):
    enabled_plugins = json.loads(os.getenv('ENABLED_PLUGINS', '[]'))
    if 'wms_geotiff_output' not in enabled_plugins:
        return None
    from qgis.core import Qgis, QgsMessageLog
    QgsMessageLog.logMessage("Plugin enabled", "WMSGeotiffOutput", Qgis.Info)
    from .wms_geotiff_output import WMSGeotiffOutput
    return WMSGeotiffOutput(serverIface)
