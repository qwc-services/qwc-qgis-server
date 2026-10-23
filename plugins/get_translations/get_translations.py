from qgis.core import *
from qgis.server import *
import json
import os
from xml.etree import ElementTree

def deep_merge(d1, d2):
    """Recursively merge two dictionaries."""
    result = d1.copy()
    for k, v in d2.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

class GetTranslationsService(QgsService):
    def __init__(self, serverIface):
        QgsService.__init__(self)
        self.serverIface = serverIface

    def name(self):
        return "GetTranslations"

    def version(self):
        return "1.0.0"

    def executeRequest(self, request, response, project):
        params = request.parameters()

        lang = params.get("LANG", "en")
        QgsMessageLog.logMessage('Lang is %s' % lang, "[GetTranslationsService]", Qgis.Info)
        projectfile = params.get("MAP", os.environ.get("QGIS_PROJECT_FILE"))
        QgsMessageLog.logMessage('Project %s' % projectfile, "[GetTranslationsService]", Qgis.Info)

        dirname = os.path.dirname(projectfile)
        filename = os.path.splitext(os.path.basename(projectfile))

        # Handle "GetTranslations" request
        QgsMessageLog.logMessage('Looking for *.ts translation files', "[GetTranslationsService]", Qgis.Info)

        response.setHeader('Content-Type', 'application/json; charset=utf-8')

        translations = {}
        ts_file = os.path.join(dirname, f"{filename[0]}_{lang}.ts")
        if not os.path.exists(ts_file):
            ts_file = os.path.join(dirname, f"{filename[0]}_{lang[0:2]}.ts")
        if os.path.exists(ts_file):
            QgsMessageLog.logMessage('Found translation %s' % ts_file, "[GetTranslationsService]", Qgis.Info)
            try:
                ts_document = ElementTree.parse(ts_file)

                # Build translation string lookup
                for context in ts_document.findall("./context"):
                    context_name = context.find('./name')
                    if context_name is None:
                        continue

                    context_name_parts = context_name.text.split(":")
                    key = None
                    if len(context_name_parts) >= 3 and context_name_parts[0] == "project" and context_name_parts[1] == "layers":
                        # replace layer id with layer name
                        maplayer = project.mapLayer(context_name_parts[2])
                        try:
                            layername = maplayer.serverProperties().shortName() or maplayer.name()
                        except:
                            layername = maplayer.shortName() or maplayer.name()

                        if len(context_name_parts) == 3:
                            ts_path = f"layertree"
                            key = layername
                        elif len(context_name_parts) == 4 and context_name_parts[3] == "fieldaliases":
                            ts_path = f"layers.{layername}.fields"
                        elif len(context_name_parts) == 4 and context_name_parts[3] == "formcontainers":
                            ts_path = f"layers.{layername}.form"
                    elif len(context_name_parts) == 2 and context_name_parts[0] == "project" and context_name_parts[1] == "layergroups":
                        ts_path = f"layertree"
                    else:
                        # Unknown ts context
                        continue

                    context_ts = translations
                    for entry in ts_path.split("."):
                        context_ts[entry] = context_ts.get(entry, {})
                        context_ts = context_ts[entry]

                    for message in context.findall("./message"):
                        source = message.find('./source')
                        translation = message.find('./translation')
                        if source is not None and translation is not None and translation.get('type', '') != "unfinished":
                            context_ts[key or source.text] = translation.text

            except Exception as e:
                QgsMessageLog.logMessage('Failed to read TS translation %s: %s' % (ts_file, str(e)), "[GetTranslationsService]", Qgis.Info)

        else:
            QgsMessageLog.logMessage('No TS translation %s found' % ts_file, "[GetTranslationsService]", Qgis.Info)

        json_file = os.path.join(dirname, f"{filename[0]}_{lang}.json")
        if not os.path.exists(json_file):
            json_file = os.path.join(dirname, f"{filename[0]}_{lang[0:2]}.json")
        if os.path.exists(json_file):
            try:
                with open(json_file) as fh:
                    translations = deep_merge(translations, json.load(fh))
            except Exception as e:
                QgsMessageLog.logMessage('Failed to read JSON translation %s: %s' % (ts_file, str(e)), "[GetTranslationsService]", Qgis.Info)

        else:
            QgsMessageLog.logMessage('No JSON translation %s found' % json_file, "[GetTranslationsService]", Qgis.Info)

        response.write(json.dumps(translations))

class GetTranslations:
    def __init__(self, serverIface):
        serverIface.serviceRegistry().registerService(GetTranslationsService(serverIface))
