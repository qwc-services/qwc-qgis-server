#
# Copyright (c) 2023-2024 Sandro Mani, Sourcepole AG
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

import os

from qgis.core import *
from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import QDomDocument
from qgis.server import *


class PrintTemplatesFilter(QgsServerFilter):
    def __init__(self, serverIface):
        super().__init__(serverIface)
        self.__layouts = []
        self.__project = None
        
    def onRequestReady(self):
        
        # Only add print layouts for GetProjectSettings and for GetPrint
        request = self.serverInterface().requestHandler()
        requestParam = request.parameter('REQUEST').upper()
        if requestParam != 'GETPRINT': # and requestParam != 'GETPROJECTSETTINGS':
            return True
        
        template = request.parameter('TEMPLATE')
        parts = template.split("/")
        subdirpath = "/".join(parts[0:-1])
        templateName = parts[-1]
        request.setParameter('TEMPLATE', templateName)
        
        projectPath = self.serverInterface().configFilePath()
        try:
            self.__project = QgsConfigCache.instance().project(projectPath)
        except:
            self.__project = None
            return True

        printLayoutDir = os.environ.get('PRINT_LAYOUT_DIR');
        if not printLayoutDir:
            QgsMessageLog.logMessage('PRINT_LAYOUT_DIR not set', 'plugin', Qgis.MessageLevel.Warning)
            return True

        QgsMessageLog.logMessage(f"Looking for templates in {printLayoutDir}", 'plugin', Qgis.MessageLevel.Info)
        
        layoutDir = os.path.join(printLayoutDir, subdirpath)
        for f in os.listdir(layoutDir):
            if not os.path.isfile(os.path.join(layoutDir, f)) or not f.lower().endswith('.qpt'):
                continue
            layoutFile = QFile(os.path.join(layoutDir, f))
            if not layoutFile.open(QIODevice.OpenModeFlag.ReadOnly):
                QgsMessageLog.logMessage(f"Failed to open '{os.path.join(layoutDir, f)}'", 'plugin', Qgis.MessageLevel.Critical)
                continue
            domDoc = QDomDocument()
            if not domDoc.setContent(layoutFile):
                QgsMessageLog.logMessage('Reading xml document failed', 'plugin', Qgis.MessageLevel.Critical)
                continue

            # Check if template name maches template parameter in request
            if domDoc.documentElement().attribute('name') != templateName:
                continue

            layout = QgsPrintLayout(self.__project)
            if not layout.readXml( domDoc.documentElement(), domDoc, QgsReadWriteContext() ):
                QgsMessageLog.logMessage('Reading layout failed', 'plugin', Qgis.MessageLevel.Critical)
            else:
                QgsMessageLog.logMessage('Reading of layout was successfull', 'plugin', Qgis.MessageLevel.Info)

            # On a name collision, addLayout() deletes the layout -> don't track it, the project's own layout is printed
            if self.__project.layoutManager().addLayout(layout):
                self.__layouts.append(layout)
            else:
                QgsMessageLog.logMessage('Could not add layout to project (layout named "%s" already exists?)' % templateName, 'plugin', Qgis.MessageLevel.Critical)
            break
        
        return True
    
    def onResponseComplete(self):
        if self.__project:
            for layout in self.__layouts:
                self.__project.layoutManager().removeLayout(layout)
            
        self.__layouts.clear()
        self.__project = None
        
        return True

class PrintTemplates:
    def __init__(self, serverIface):
        self.iface = serverIface
        serverIface.registerFilter(PrintTemplatesFilter(serverIface))
