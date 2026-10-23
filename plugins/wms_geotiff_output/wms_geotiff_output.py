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

from qgis.core import *
from qgis.server import *
from qgis.PyQt.QtGui import QImage, qRed, qGreen, qBlue, qAlpha
from qgis.PyQt.QtCore import QByteArray
import xml.dom.minidom
from xml.dom.minidom import parseString
from osgeo import gdal
import numpy

class WMSGeotiffFilter(QgsServerFilter):
    def __init__(self, serverIface):
        super(WMSGeotiffFilter, self).__init__(serverIface)
        self.__isFormatTiff = False #track format since we have to make the server return PNG
        
    def onRequestReady(self):
        request = self.serverInterface().requestHandler()
        if request.parameter('SERVICE').upper() == 'WMS' and request.parameter('REQUEST').upper() == 'GETMAP':
            if request.parameter('FORMAT').upper() == 'IMAGE/TIFF':
                request.setParameter('FORMAT','image/png')
                self.__isFormatTiff = True
        return True
        
    def onResponseComplete(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        #Only handle WMS requests
        if request.parameter('SERVICE').upper() != 'WMS':
            return True
        
        requestParam = request.parameter('REQUEST').upper()
        if requestParam == 'GETCAPABILITIES' or requestParam == 'GETPROJECTSETTINGS':
            self.modifyCapabilities(request)
        elif requestParam == 'GETMAP':
            if self.__isFormatTiff:
                self.modifyGetMap(request)
        
        self.__isFormatTiff = False
        return True
    
    def writeGeorefInfo(self, geoTiffDS, extentString, crsString, width, height):
        coordStrings = extentString.split(',')
        
        #Convert extent string to rectangle
        if len(coordStrings) < 4:
            return
        
        try:
            extent = QgsRectangle(float(coordStrings[0]), float(coordStrings[1]), float(coordStrings[2]), float(coordStrings[3]))
        except ValueError:
            return
        
        crs = QgsCoordinateReferenceSystem(crsString)
        
        try:
            geoTiffDS.SetGeoTransform([extent.xMinimum(), extent.width() / float(width), 0, extent.yMaximum(), 0, -( extent.height() / float(height) )])
        except ValueError:
            return
            
        if crs.isValid():
            geoTiffDS.SetProjection(crs.toWkt())
    
    def writeImageToGDALDataSource(self, ds, img):
        redBand = ds.GetRasterBand( 1 )
        greenBand = ds.GetRasterBand( 2 )
        blueBand = ds.GetRasterBand( 3 )
        alphaBand = ds.GetRasterBand( 4 )
        
        w = img.width()
        h = img.height()
        nPixels = img.width() * img.height()
        
        redData = numpy.zeros((h, w), dtype=numpy.uint8)
        greenData = numpy.zeros((h, w), dtype=numpy.uint8)
        blueData = numpy.zeros((h, w), dtype=numpy.uint8)
        alphaData = numpy.zeros((h, w), dtype=numpy.uint8)
        
        for i in range (h):
            for j in range (w):
                rgb = img.pixel(j,i)
                redData[i,j] = qRed(rgb)
                greenData[i,j] = qGreen(rgb)
                blueData[i,j] = qBlue(rgb)
                alphaData[i,j] = qAlpha(rgb)
        
        redBand.WriteArray( redData )
        redBand.FlushCache()
        greenBand.WriteArray( greenData )
        greenBand.FlushCache()
        blueBand.WriteArray( blueData )
        blueBand.FlushCache()
        alphaBand.WriteArray( alphaData )
        alphaBand.FlushCache()
    
    def modifyGetMap(self, requestHandler):
        pngData = requestHandler.body()
        requestHandler.clear()
        
        img = QImage()
        img.loadFromData(pngData,'png')
        
        gtiffDriver = gdal.GetDriverByName('GTiff')
        vsiPath = '/vsimem/wms.tif'
        gtiffDS = gtiffDriver.Create(vsiPath, img.width(), img.height(), 4, gdal.GDT_Byte, ['COMPRESS=LZW'] )
        if not gtiffDS:
            return
        
        extentString = requestHandler.parameter('BBOX')
        crsString = requestHandler.parameter('CRS')
        if not crsString:
            crsString = requestHandler.parameter('SRS')
        self.writeGeorefInfo(gtiffDS, extentString, crsString,img.width(), img.height())
        self.writeImageToGDALDataSource(gtiffDS, img)
        gtiffDS = None
        
        #read from vsi
        stat = gdal.VSIStatL(vsiPath, gdal.VSI_STAT_SIZE_FLAG)
        vsifile = gdal.VSIFOpenL(vsiPath, 'r')
        tiffBytes = gdal.VSIFReadL(1, stat.size, vsifile)
        
        requestHandler.setResponseHeader( 'Content-Type', 'image/tiff' )
        requestHandler.appendBody(tiffBytes)
    
    def modifyCapabilities(self, requestHandler):
        capabilitiesDoc = parseString(str(requestHandler.body(), encoding='utf-8'))
        
        getMapElems = capabilitiesDoc.getElementsByTagName('GetMap')
        if len(getMapElems) < 1:
            QgsMessageLog.logMessage("GetMap element not found", 'plugin', Qgis.Info)
            return
        getMapElem = getMapElems[0]
        formatElem = capabilitiesDoc.createElement('Format')
        formatText = capabilitiesDoc.createTextNode('image/tiff')
        formatElem.appendChild(formatText)
        #Add Format tag as first entry in the format section
        existingFormatElems = getMapElem.getElementsByTagName('Format')
        if len(existingFormatElems) > 0:
            getMapElem.insertBefore(formatElem, existingFormatElems[0])
        else:
            getMapElem.appendChild(formatElem)
        
        #Set modified XML as response to request handler
        requestHandler.clear()
        requestHandler.setResponseHeader('Content-type', 'text/xml; charset=utf-8')
        xmlString = capabilitiesDoc.toprettyxml()
        xmlString = '<?xml version="1.0" encoding="utf-8"?>\n' + \
            '\n'.join(xmlString.split('\n')[1:])
        requestHandler.appendBody(bytes(xmlString, 'utf-8'))
        
class WMSGeotiffOutput:
    def __init__(self, serverIface):
        self.iface = serverIface
        serverIface.registerFilter(WMSGeotiffFilter(serverIface))
