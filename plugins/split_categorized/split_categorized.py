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

from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsExpressionContextUtils,
    QgsGraduatedSymbolRenderer,
    QgsLayerTree,
    QgsMessageLog,
    QgsRuleBasedRenderer
)
from qgis.server import QgsServerFilter, QgsConfigCache, QgsServerSettings
from xml.etree import ElementTree


class SplitCategorizedLayersFilter(QgsServerFilter):
    """QGIS Server SplitCategorizedLayers plugin."""

    def __init__(self, server_iface):
        super().__init__(server_iface)

    def onRequestReady(self):
        projectPath = self.serverInterface().configFilePath()
        try:
            qgs_project = QgsConfigCache.instance().project(projectPath)
        except:
            return True
        # Skip non-existing project
        if not qgs_project:
            return True

        # Walk through layer tree, split categorized layers as required
        root = qgs_project.layerTreeRoot()
        # QgsMessageLog.logMessage(
        #     f"XXX Before = %s" % (root.dump()), "SplitCategorizedLayer", Qgis.MessageLevel.Info
        # )
        self.splitCounter = 0
        for (idx, child) in enumerate(root.children()):
            self.split_layers_in_tree(child, root, idx, qgs_project)

        # qgs_project.write(projectPath + "_split.qgs")

        # QgsMessageLog.logMessage(
        #     f"XXX After = %s" % (root.dump()), "SplitCategorizedLayer", Qgis.MessageLevel.Info
        # )
        return True

    def onSendResponse(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()
        if params.get('SERVICE', "").upper() == 'WMS' and \
            params.get('REQUEST', "").upper() == 'GETPROJECTSETTINGS'\
        :
            return False
        return True

    def onResponseComplete(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()
        if params.get('SERVICE', "").upper() != 'WMS' or \
            params.get('REQUEST', "").upper() != 'GETPROJECTSETTINGS' or \
            request.exceptionRaised() \
        :
            return True

        server_settings = QgsServerSettings()
        server_settings.load()
        QgsConfigCache.initialize(server_settings)
        config_cache = QgsConfigCache.instance()
        map_file = server_settings.projectFile()
        if not map_file:
            map_file = self.serverInterface().requestHandler().parameter("MAP")
        try:
            qgs_project = config_cache.project(map_file)
        except:
            qgs_project = None
        if not qgs_project:
            return True

        data = request.body()
        ElementTree.register_namespace('', 'http://www.opengis.net/wms')
        ElementTree.register_namespace('qgs', 'http://www.qgis.org/wms')
        ElementTree.register_namespace('sld', 'http://www.opengis.net/sld')
        ElementTree.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        doc = ElementTree.fromstring(data)

        # use default namespace for XML search
        # namespace dict
        ns = {'ns': 'http://www.opengis.net/wms'}
        # namespace prefix
        np = 'ns:'
        if not doc.tag.startswith('{http://'):
            # do not use namespace
            ns = {}
            np = ''

        for layer in doc.findall('.//%sLayer' % np, ns):
            nameEl = layer.find('%sName' % np, ns)
            if nameEl is None:
                continue
            name = nameEl.text
            qgs_layers = qgs_project.mapLayersByShortName(name)
            if len(qgs_layers) != 1:
                continue
            context = QgsExpressionContextUtils.layerScope(qgs_layers[0])
            if context.variable("is_category_sublayer") == "true":
                layer.set('category_sublayer', '1')
                if context.variable("category_visibility") == "false":
                    layer.set('visibilityChecked', '0')
                else:
                    layer.set('visibilityChecked', '1')

        request.clearBody()
        request.appendBody(ElementTree.tostring(doc, encoding='UTF-8', xml_declaration=True))
        return True

    def split_layers_in_tree(self, node, parent, pos, qgs_project):

        if QgsLayerTree.isLayer(node):
            layer = node.layer()
            context = QgsExpressionContextUtils.layerScope(layer)
            if (
                layer is None or not layer.isValid()
                or not context.hasVariable("convert_categorized_layer")
                or context.variable("convert_categorized_layer").lower() != "true"
            ):
                return

            layerRenderer = layer.renderer()
            layerSymbols = layerRenderer.legendSymbolItems()

            QgsMessageLog.logMessage(
                f"Spliting {layer.name()} into {len(layerSymbols)} layers",
                "SplitCategorizedLayer",
                Qgis.MessageLevel.Info,
            )

            group = parent.insertGroup(pos, layer.name())
            category_shortname = layer.serverProperties().shortName() or "_sl"
            for symbol in layerSymbols:
                category_layer = layer.clone()
                category_layer.serverProperties().setTitle(symbol.label())
                category_layer.setName(symbol.label())
                category_layer.serverProperties().setShortName(f"{category_shortname}_{self.splitCounter}")
                self.splitCounter += 1
                category_layer.setCrs(layer.crs())
                QgsExpressionContextUtils.setLayerVariable(category_layer, "convert_categorized_layer", "false")
                QgsExpressionContextUtils.setLayerVariable(category_layer, "is_category_sublayer", "true")

                if layerRenderer.legendSymbolItemsCheckable():
                    visible = layerRenderer.legendSymbolItemChecked(symbol.ruleKey())
                QgsExpressionContextUtils.setLayerVariable(category_layer, "category_visibility", "true" if visible else "false")

                cat_renderer = QgsRuleBasedRenderer.convertFromRenderer(layerRenderer, layer)

                category_layer.setRenderer(cat_renderer)
                root_rule = category_layer.renderer().rootRule()
                for rule in root_rule.children():
                    if rule.label() != symbol.label():
                        root_rule.removeChild(rule)
                    else:
                        # Ensure layer and symbol rule is checked
                        cat_renderer.checkLegendSymbolItem(rule.ruleKey(), True)


                qgs_project.addMapLayer(category_layer, False)
                group.addLayer(category_layer)

            qgs_project.removeMapLayer(layer)

        else:
            for (idx, child) in enumerate(node.children()):
                self.split_layers_in_tree(child, node, idx, qgs_project)

class SplitCategorizedLayers:
    """
    Add support to split categorized layers into
    multiple layers.
    """

    def __init__(self, server_iface):
        """Register the filter"""
        split_categorized_layers = SplitCategorizedLayersFilter(server_iface)
        server_iface.registerFilter(split_categorized_layers, 1)
