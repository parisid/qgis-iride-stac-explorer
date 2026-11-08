# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any, Optional
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsRasterLayer, QgsVectorLayer, QgsProject, QgsMessageLog, Qgis,
    QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsRectangle,
    QgsSimpleFillSymbolLayer, QgsFillSymbol, QgsSingleSymbolRenderer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform
)
from qgis.gui import QgisInterface

class RasterLoader:
    """Carica layer raster remoti in QGIS in streaming (Cloud Optimized GeoTIFF, JPEG2000, ecc.) o da file locale."""

    @staticmethod
    def normalize_vsi_path(url: str) -> str:
        """Converte URL http/https/s3 nel rispettivo percorso virtuale GDAL (/vsicurl/ o /vsis3/)."""
        clean_url = url.strip()
        if clean_url.startswith("/vsi"):
            return clean_url

        if clean_url.startswith("s3://"):
            # Converte s3://bucket/key in https://bucket.s3.amazonaws.com/key oppure /vsis3/
            bucket_and_key = clean_url[5:]
            parts = bucket_and_key.split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            http_url = f"https://{bucket}.s3.amazonaws.com/{key}"
            return f"/vsicurl/{http_url}"

        if clean_url.startswith("http://") or clean_url.startswith("https://"):
            return f"/vsicurl/{clean_url}"

        return clean_url

    @staticmethod
    def load_cog_streaming(signed_url: str, layer_name: str) -> bool:
        vsi_path = RasterLoader.normalize_vsi_path(signed_url)

        layer = QgsRasterLayer(vsi_path, layer_name, "gdal")
        if not layer.isValid():
            # Tentativo di fallback con /vsis3/ se l'url originale era su S3
            if "s3.amazonaws.com" in vsi_path or signed_url.startswith("s3://"):
                s3_key = signed_url[5:] if signed_url.startswith("s3://") else signed_url.split("s3.amazonaws.com/")[-1]
                vsi_s3_path = f"/vsis3/{s3_key}"
                layer_s3 = QgsRasterLayer(vsi_s3_path, layer_name, "gdal")
                if layer_s3.isValid():
                    RasterLoader.optimize_raster_symbology(layer_s3)
                    QgsProject.instance().addMapLayer(layer_s3)
                    return True

            err_detail = layer.error().message() if layer.error() else "Nessun dettaglio errore GDAL disponibile"
            QgsMessageLog.logMessage(
                f"Impossibile caricare il raster remoto: {vsi_path}. Errore GDAL: {err_detail}", 
                "IRIDE Explorer", 
                Qgis.Critical
            )
            return False

        RasterLoader.optimize_raster_symbology(layer)
        QgsProject.instance().addMapLayer(layer)
        return True

    @staticmethod
    def load_local_raster(filepath: str, layer_name: str) -> bool:
        layer = QgsRasterLayer(filepath, layer_name, "gdal")
        if not layer.isValid():
            QgsMessageLog.logMessage(
                f"Impossibile caricare il raster locale: {filepath}. Errore GDAL: {layer.error().message()}", 
                "IRIDE Explorer", 
                Qgis.Critical
            )
            return False

        RasterLoader.optimize_raster_symbology(layer)
        QgsProject.instance().addMapLayer(layer)
        return True

    @staticmethod
    def optimize_raster_symbology(layer: QgsRasterLayer):
        """Applica contrast enhancement ottimale (stretch cumulativo 2%-98%) in base al numero di bande."""
        try:
            renderer = layer.renderer()
            if not renderer:
                return

            pipe = layer.pipe()
            if not pipe:
                return

            # Se il layer è multibanda (es. RGB True Color), ottimizza i contrasti sui canali
            if layer.bandCount() >= 3:
                layer.setDefaultContrastEnhancement()
            elif layer.bandCount() == 1:
                # Monobanda (es. SAR backscatter o indice spettrale)
                layer.setDefaultContrastEnhancement()
            layer.triggerRepaint()
        except Exception as e:
            QgsMessageLog.logMessage(f"Ottimizzazione simbologia non applicata: {str(e)}", "IRIDE Explorer", Qgis.Info)


class FootprintManager:
    """Gestisce il layer vettoriale in memoria per i footprint (geometria/BBOX) dei risultati STAC."""

    LAYER_NAME = "IRIDE STAC Footprints"

    @classmethod
    def get_or_create_layer(cls) -> QgsVectorLayer:
        project = QgsProject.instance()
        for lyr in project.mapLayers().values():
            if isinstance(lyr, QgsVectorLayer) and lyr.name() == cls.LAYER_NAME:
                return lyr

        layer = QgsVectorLayer("Polygon?crs=epsg:4326", cls.LAYER_NAME, "memory")
        pr = layer.dataProvider()
        pr.addAttributes([
            QgsField("stac_id", QVariant.String),
            QgsField("collection", QVariant.String),
            QgsField("datetime", QVariant.String),
            QgsField("cloud_cover", QVariant.String),
            QgsField("level", QVariant.String),
        ])
        layer.updateFields()

        # Stile semi-trasparente con bordo evidente
        symbol = QgsFillSymbol.createSimple({
            "color": "0,150,255,45",
            "outline_color": "0,110,210,230",
            "outline_width": "0.6"
        })
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        project.addMapLayer(layer)
        return layer

    @classmethod
    def update_footprints(cls, features: List[Dict[str, Any]]) -> Optional[QgsVectorLayer]:
        if not features:
            return None

        layer = cls.get_or_create_layer()
        pr = layer.dataProvider()
        pr.truncate()

        qgs_features = []
        for item in features:
            geom = cls._extract_geometry(item)
            if not geom or geom.isEmpty():
                continue

            props = item.get("properties", {})
            qf = QgsFeature(layer.fields())
            qf.setGeometry(geom)
            qf.setAttributes([
                str(item.get("id", "")),
                str(item.get("collection", "")),
                str(props.get("datetime", "")),
                str(props.get("eo:cloud_cover", "N/D")),
                str(props.get("processing:level", "N/D")),
            ])
            qgs_features.append(qf)

        if qgs_features:
            pr.addFeatures(qgs_features)
        layer.updateExtents()
        layer.triggerRepaint()
        return layer

    @classmethod
    def highlight_and_zoom(cls, item: Dict[str, Any], iface: QgisInterface, zoom: bool = True):
        geom = cls._extract_geometry(item)
        if not geom or geom.isEmpty():
            return

        # Seleziona la feature corrispondente nel layer footprints se presente
        item_id = str(item.get("id", ""))
        project = QgsProject.instance()
        for lyr in project.mapLayers().values():
            if isinstance(lyr, QgsVectorLayer) and lyr.name() == cls.LAYER_NAME:
                ids_to_select = [f.id() for f in lyr.getFeatures() if f["stac_id"] == item_id]
                lyr.selectByIds(ids_to_select)
                break

        if zoom and iface and iface.mapCanvas():
            canvas = iface.mapCanvas()
            src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            tgt_crs = canvas.mapSettings().destinationCrs()
            transform = QgsCoordinateTransform(src_crs, tgt_crs, project)
            bbox = transform.transformBoundingBox(geom.boundingBox())
            bbox.scale(1.25)
            canvas.setExtent(bbox)
            canvas.refresh()

    @staticmethod
    def _extract_geometry(item: Dict[str, Any]) -> Optional[QgsGeometry]:
        geom_dict = item.get("geometry")
        if geom_dict and geom_dict.get("type") == "Polygon":
            coords = geom_dict.get("coordinates", [])
            if coords and coords[0]:
                ring = [QgsPointXY( float(pt[0]), float(pt[1]) ) for pt in coords[0]]
                return QgsGeometry.fromPolygonXY([ring])

        bbox = item.get("bbox")
        if bbox and len(bbox) >= 4:
            rect = QgsRectangle(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
            return QgsGeometry.fromRect(rect)

        return None
