# -*- coding: utf-8 -*-
from ..core.qt_compat import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QCheckBox, QAbstractItemView, QSpinBox,
    QGroupBox, QFileDialog, QProgressBar, Qt, QDate, QPixmap, QImage
)
from qgis.core import (
    QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, 
    QgsApplication, QgsMessageLog, Qgis
)
from qgis.gui import QgisInterface
from ..core.config import ConfigManager
from ..core.stac_client import StacClient
from ..core.signer_client import SignerClient
from ..core.raster_loader import RasterLoader, FootprintManager
from ..core.async_tasks import AsyncWorkerTask, DownloadAssetTask
from ..core.i18n import tr
from .settings_dialog import SettingsDialog

class IrideDockWidget(QDockWidget):
    def __init__(self, iface: QgisInterface, parent=None):
        super().__init__("IRIDE STAC Explorer", parent)
        self.iface = iface
        self.stac_client = StacClient()
        self.current_features = []
        self._active_tasks = []
        self._next_link = None
        self._last_search_params = {}

        self.init_ui()
        self.refresh_collections()

    def _submit_task(self, task):
        """Mantiene un riferimento Python al QgsTask fino al completamento per evitare garbage collection prematura."""
        self._active_tasks.append(task)
        orig_finished = task.on_finished

        def _wrapped_finished(result, exception):
            if task in self._active_tasks:
                self._active_tasks.remove(task)
            if orig_finished:
                orig_finished(result, exception)

        task.on_finished = _wrapped_finished
        QgsApplication.taskManager().addTask(task)

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        # Barra superiore
        top_bar = QHBoxLayout()
        self.btn_settings = QPushButton(tr("BTN_SETTINGS"))
        self.btn_settings.clicked.connect(self.open_settings)
        self.lbl_endpoint_status = QLabel()
        self.update_endpoint_badge()
        top_bar.addWidget(self.btn_settings)
        top_bar.addWidget(self.lbl_endpoint_status)
        layout.addLayout(top_bar)

        # Filtri Collezione, BBOX, Data, Copertura Nuvolosa e Limite Risultati
        filter_group = QVBoxLayout()

        coll_layout = QHBoxLayout()
        coll_layout.addWidget(QLabel(tr("LBL_COLLECTION")))
        self.cmb_collection = QComboBox()
        self.cmb_collection.addItem(tr("ALL_COLLECTIONS"), None)
        coll_layout.addWidget(self.cmb_collection, stretch=1)
        self.btn_refresh_collections = QPushButton("🔄")
        self.btn_refresh_collections.setToolTip(tr("TOOLTIP_REFRESH_COLLECTIONS"))
        self.btn_refresh_collections.setFixedWidth(32)
        self.btn_refresh_collections.clicked.connect(self.refresh_collections)
        coll_layout.addWidget(self.btn_refresh_collections)
        filter_group.addLayout(coll_layout)

        self.chk_use_canvas_extent = QCheckBox(tr("CHK_CANVAS_EXTENT"))
        self.chk_use_canvas_extent.setChecked(True)
        filter_group.addWidget(self.chk_use_canvas_extent)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel(tr("LBL_DATE_FROM")))
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-3))
        self.date_from.setCalendarPopup(True)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel(tr("LBL_DATE_TO")))
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(self.date_to)
        filter_group.addLayout(date_layout)

        opts_layout = QHBoxLayout()
        self.chk_cloud_cover = QCheckBox(tr("CHK_CLOUD_COVER"))
        self.chk_cloud_cover.setChecked(False)
        self.spn_cloud_cover = QSpinBox()
        self.spn_cloud_cover.setRange(0, 100)
        self.spn_cloud_cover.setValue(30)
        self.spn_cloud_cover.setEnabled(False)
        self.chk_cloud_cover.toggled.connect(self.spn_cloud_cover.setEnabled)
        opts_layout.addWidget(self.chk_cloud_cover)
        opts_layout.addWidget(self.spn_cloud_cover)

        opts_layout.addWidget(QLabel(tr("LBL_LIMIT")))
        self.cmb_limit = QComboBox()
        self.cmb_limit.addItems(["10", "25", "50", "100"])
        self.cmb_limit.setCurrentText("50")
        opts_layout.addWidget(self.cmb_limit)
        filter_group.addLayout(opts_layout)

        footprint_layout = QHBoxLayout()
        self.chk_show_footprints = QCheckBox(tr("CHK_SHOW_FOOTPRINTS"))
        self.chk_show_footprints.setChecked(True)
        self.btn_zoom_footprint = QPushButton(tr("BTN_ZOOM_FOOTPRINT"))
        self.btn_zoom_footprint.setEnabled(False)
        self.btn_zoom_footprint.clicked.connect(self.zoom_to_selected_feature)
        footprint_layout.addWidget(self.chk_show_footprints)
        footprint_layout.addWidget(self.btn_zoom_footprint)
        filter_group.addLayout(footprint_layout)

        layout.addLayout(filter_group)

        # Ricerca
        self.btn_search = QPushButton(tr("BTN_SEARCH"))
        self.btn_search.setStyleSheet("font-weight: bold; padding: 6px;")
        self.btn_search.clicked.connect(self.run_search)
        layout.addWidget(self.btn_search)

        # Tabella Risultati
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            tr("COL_ID"), tr("COL_DATETIME"), tr("COL_CLOUD"), tr("COL_LEVEL")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.selectionModel().selectionChanged.connect(self.on_item_selected)
        layout.addWidget(self.table)

        # Paginazione "Carica altri risultati"
        self.btn_load_more = QPushButton(tr("BTN_LOAD_MORE"))
        self.btn_load_more.setEnabled(False)
        self.btn_load_more.clicked.connect(self.load_more_results)
        layout.addWidget(self.btn_load_more)

        # Pannello Anteprima Thumbnail
        grp_preview = QGroupBox(tr("GRP_PREVIEW"))
        preview_layout = QVBoxLayout(grp_preview)
        self.lbl_thumbnail = QLabel(tr("PREVIEW_SELECT_ITEM"))
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setMinimumHeight(125)
        self.lbl_thumbnail.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;")
        preview_layout.addWidget(self.lbl_thumbnail)
        layout.addWidget(grp_preview)

        # Selezione Asset, Streaming COG e Download Locale
        asset_layout = QVBoxLayout()
        h_asset_sel = QHBoxLayout()
        h_asset_sel.addWidget(QLabel(tr("LBL_ASSET")))
        self.cmb_assets = QComboBox()
        self.cmb_assets.currentIndexChanged.connect(self.on_asset_changed)
        h_asset_sel.addWidget(self.cmb_assets, stretch=1)
        asset_layout.addLayout(h_asset_sel)

        h_asset_btns = QHBoxLayout()
        self.btn_load_raster = QPushButton(tr("BTN_STREAM_COG"))
        self.btn_load_raster.setToolTip(tr("TOOLTIP_STREAM_COG"))
        self.btn_load_raster.setEnabled(False)
        self.btn_load_raster.clicked.connect(self.load_selected_asset_streaming)
        h_asset_btns.addWidget(self.btn_load_raster)

        self.btn_download_raster = QPushButton(tr("BTN_DOWNLOAD_LOCAL"))
        self.btn_download_raster.setToolTip(tr("TOOLTIP_DOWNLOAD_LOCAL"))
        self.btn_download_raster.setEnabled(False)
        self.btn_download_raster.clicked.connect(self.download_selected_asset_local)
        h_asset_btns.addWidget(self.btn_download_raster)
        asset_layout.addLayout(h_asset_btns)

        self.progress_download = QProgressBar()
        self.progress_download.setVisible(False)
        asset_layout.addWidget(self.progress_download)

        layout.addLayout(asset_layout)

        # Disclaimer
        lbl_disclaimer = QLabel(tr("DISCLAIMER_SHORT"))
        lbl_disclaimer.setWordWrap(True)
        layout.addWidget(lbl_disclaimer)

        self.setWidget(container)

    def update_endpoint_badge(self):
        profile = ConfigManager.get_endpoint_profile()
        if profile == ConfigManager.PROFILE_EARTH_SEARCH:
            self.lbl_endpoint_status.setText(f"<b>{tr('STATUS_TEST')}</b>")
            self.lbl_endpoint_status.setStyleSheet("color: #0275d8; font-weight: bold;")
        else:
            has_key = bool(ConfigManager.get_api_key())
            status_text = tr("STATUS_IRIDE_OK") if has_key else tr("STATUS_IRIDE_NO_KEY")
            color = "#5cb85c" if has_key else "#d9534f"
            self.lbl_endpoint_status.setText(f"<b>{status_text}</b>")
            self.lbl_endpoint_status.setStyleSheet(f"color: {color}; font-weight: bold;")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.update_endpoint_badge()
            self.refresh_collections()

    def refresh_collections(self):
        self.btn_refresh_collections.setEnabled(False)

        def worker():
            return self.stac_client.get_collections()

        def on_done(collections, exception):
            self.btn_refresh_collections.setEnabled(True)
            current_id = self.cmb_collection.currentData()
            self.cmb_collection.clear()
            self.cmb_collection.addItem(tr("ALL_COLLECTIONS"), None)
            if exception or not collections:
                return
            for col in collections:
                cid = col.get("id")
                title = col.get("title") or cid
                if cid:
                    self.cmb_collection.addItem(f"{cid} — {title}", cid)
            if current_id:
                idx = self.cmb_collection.findData(current_id)
                if idx >= 0:
                    self.cmb_collection.setCurrentIndex(idx)

        task = AsyncWorkerTask("Caricamento Collezioni STAC", worker, on_done)
        self._submit_task(task)

    def get_current_bbox_wgs84(self):
        canvas = self.iface.mapCanvas()
        extent = canvas.extent()
        src_crs = canvas.mapSettings().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(src_crs, tgt_crs, QgsProject.instance())
        wgs_extent = transform.transformBoundingBox(extent)
        
        # Validazione e controllo scala canvas
        width_deg = abs(wgs_extent.xMaximum() - wgs_extent.xMinimum())
        height_deg = abs(wgs_extent.yMaximum() - wgs_extent.yMinimum())
        if width_deg > 60.0 or height_deg > 60.0:
            QgsMessageLog.logMessage(
                f"Estensione canvas molto ampia ({width_deg:.1f}° x {height_deg:.1f}°). La ricerca potrebbe restituire molti risultati.",
                "IRIDE Explorer",
                Qgis.Warning
            )

        return [round(wgs_extent.xMinimum(), 6), round(wgs_extent.yMinimum(), 6),
                round(wgs_extent.xMaximum(), 6), round(wgs_extent.yMaximum(), 6)]

    def run_search(self):
        self.btn_search.setEnabled(False)
        self.btn_search.setText(tr("SEARCHING"))
        self.btn_load_more.setEnabled(False)
        self.table.setRowCount(0)
        self.cmb_assets.clear()
        self.btn_load_raster.setEnabled(False)
        self.btn_download_raster.setEnabled(False)
        self.btn_zoom_footprint.setEnabled(False)
        self.lbl_thumbnail.setPixmap(QPixmap())
        self.lbl_thumbnail.setText(tr("PREVIEW_SELECT_ITEM"))

        bbox = self.get_current_bbox_wgs84() if self.chk_use_canvas_extent.isChecked() else None
        d_from = self.date_from.date().toString(Qt.ISODate) + "T00:00:00Z"
        d_to = self.date_to.date().toString(Qt.ISODate) + "T23:59:59Z"
        time_range = f"{d_from}/{d_to}"

        selected_coll = self.cmb_collection.currentData()
        collections = [selected_coll] if selected_coll else None
        max_cloud = float(self.spn_cloud_cover.value()) if self.chk_cloud_cover.isChecked() else None
        limit = int(self.cmb_limit.currentText())

        self._last_search_params = {
            "bbox": bbox,
            "collections": collections,
            "datetime_range": time_range,
            "max_cloud_cover": max_cloud,
            "limit": limit
        }

        def worker_func():
            return self.stac_client.search(**self._last_search_params)

        def on_completed(result, exception):
            self.btn_search.setEnabled(True)
            self.btn_search.setText(tr("BTN_SEARCH"))
            if exception:
                QMessageBox.critical(self, "Errore Ricerca STAC", f"Si è verificato un errore:\n{str(exception)}")
                return

            res_dict = result or {}
            self.current_features = res_dict.get("features", [])
            self._next_link = StacClient.extract_next_link(res_dict)
            self.btn_load_more.setEnabled(self._next_link is not None)

            self.populate_table(self.current_features)
            if self.chk_show_footprints.isChecked() and self.current_features:
                FootprintManager.update_footprints(self.current_features)

        task = AsyncWorkerTask("Interrogazione Catalogo STAC", worker_func, on_completed)
        self._submit_task(task)

    def load_more_results(self):
        if not self._next_link:
            return

        self.btn_load_more.setEnabled(False)
        self.btn_load_more.setText(tr("LOADING_MORE"))

        next_url = self._next_link.get("href")
        next_body = self._next_link.get("body")
        collections = self._last_search_params.get("collections")
        max_cloud = self._last_search_params.get("max_cloud_cover")

        def worker_func():
            return self.stac_client.search(
                next_url=next_url,
                next_body=next_body,
                collections=collections,
                max_cloud_cover=max_cloud
            )

        def on_completed(result, exception):
            self.btn_load_more.setText(tr("BTN_LOAD_MORE"))
            if exception:
                QMessageBox.warning(self, "Paginazione STAC", f"Impossibile caricare i risultati successivi:\n{str(exception)}")
                self.btn_load_more.setEnabled(True)
                return

            res_dict = result or {}
            new_features = res_dict.get("features", [])
            self._next_link = StacClient.extract_next_link(res_dict)
            self.btn_load_more.setEnabled(self._next_link is not None)

            self.current_features.extend(new_features)
            self.populate_table(self.current_features)
            if self.chk_show_footprints.isChecked() and self.current_features:
                FootprintManager.update_footprints(self.current_features)

        task = AsyncWorkerTask("Paginazione Catalogo STAC", worker_func, on_completed)
        self._submit_task(task)

    def populate_table(self, features):
        self.table.setRowCount(len(features))
        for row, feat in enumerate(features):
            props = feat.get("properties", {})
            feat_id = feat.get("id", "N/A")
            dt = props.get("datetime", "N/A")
            raw_cloud = props.get("eo:cloud_cover")
            cloud = f"{raw_cloud}%" if raw_cloud is not None else "N/D"
            level = props.get("processing:level", "N/D")

            self.table.setItem(row, 0, QTableWidgetItem(feat_id))
            self.table.setItem(row, 1, QTableWidgetItem(str(dt)))
            self.table.setItem(row, 2, QTableWidgetItem(str(cloud)))
            self.table.setItem(row, 3, QTableWidgetItem(str(level)))

    def on_item_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.cmb_assets.clear()
            self.btn_load_raster.setEnabled(False)
            self.btn_download_raster.setEnabled(False)
            self.btn_zoom_footprint.setEnabled(False)
            self.lbl_thumbnail.setPixmap(QPixmap())
            self.lbl_thumbnail.setText(tr("PREVIEW_SELECT_ITEM"))
            return

        row = selected_rows[0].row()
        feature = self.current_features[row]
        assets = feature.get("assets", {})

        self.cmb_assets.blockSignals(True)
        self.cmb_assets.clear()
        thumbnail_url = None
        best_score = -1
        preferred_index = 0
        current_idx = 0

        # Mappa dei punteggi di priorità per preselezionare sempre l'immagine raster principale
        # Scala di preferenza: True Color / RGB composito > bande SAR primarie > bande ottiche RGB > altri raster dati
        priority_weights = {
            "visual": 100,
            "tci": 95,
            "true_color": 95,
            "rgb": 90,
            "overview": 85,
            "vv": 80,
            "vh": 78,
            "hh": 75,
            "hv": 73,
            "red": 70,
            "green": 68,
            "blue": 65,
            "nir": 60,
            "data": 55,
            "dem": 55,
            "elevation": 55
        }

        for key, asset in assets.items():
            title = asset.get("title", key)
            roles = asset.get("roles", [])
            asset_type = asset.get("type", "")
            href = asset.get("href", "")

            # Individua thumbnail
            if key == "thumbnail" or "thumbnail" in roles or "preview" in href:
                if not thumbnail_url and ("image/" in asset_type or href.endswith((".png", ".jpg", ".jpeg"))):
                    thumbnail_url = href

            # Distingue tra immagini raster e file di metadati testuali/accessori
            is_metadata = (
                "metadata" in roles or
                asset_type in ("application/xml", "application/json", "text/xml", "text/plain") or
                href.endswith((".xml", ".json", ".safe", ".txt", ".cpg"))
            )

            if is_metadata:
                label = f"📄 [Meta] {key} ({title})"
            else:
                label = f"🖼 {key} ({title})"
                # Calcola il punteggio di utilità di questo raster
                score = 10  # Punteggio base per qualsiasi immagine raster
                if "data" in roles:
                    score += 20
                if "visual" in roles or "overview" in roles:
                    score += 50

                k_lower = key.lower()
                for p_key, weight in priority_weights.items():
                    if p_key in k_lower:
                        score = max(score, weight)

                # Penalizza maschere QA o coefficienti se presenti altre bande visive
                if "qa" in k_lower or "mask" in k_lower or "ang" in k_lower:
                    score = min(score, 5)

                if score > best_score:
                    best_score = score
                    preferred_index = current_idx

            self.cmb_assets.addItem(label, asset)
            current_idx += 1

        self.cmb_assets.blockSignals(False)
        if self.cmb_assets.count() > 0:
            self.cmb_assets.setCurrentIndex(preferred_index)
            self.on_asset_changed()

        self.btn_zoom_footprint.setEnabled(True)

        if self.chk_show_footprints.isChecked():
            FootprintManager.highlight_and_zoom(feature, self.iface, zoom=False)

        self.load_thumbnail_preview(thumbnail_url)

    def on_asset_changed(self):
        asset_data = self.cmb_assets.currentData()
        if not asset_data:
            self.btn_load_raster.setEnabled(False)
            self.btn_download_raster.setEnabled(False)
            return

        roles = asset_data.get("roles", [])
        asset_type = asset_data.get("type", "")
        href = asset_data.get("href", "")

        is_metadata = (
            "metadata" in roles or
            asset_type in ("application/xml", "application/json", "text/xml", "text/plain") or
            href.endswith((".xml", ".json", ".safe", ".txt"))
        )

        # Se è un file di metadati non raster, disabilita il caricamento streaming GDAL
        can_stream = not is_metadata
        self.btn_load_raster.setEnabled(can_stream)
        self.btn_download_raster.setEnabled(True)  # I metadati si possono comunque scaricare se serve
        if not can_stream:
            self.btn_load_raster.setToolTip("Questo asset è un file di metadati testuale (XML/JSON), non un'immagine raster.")
        else:
            self.btn_load_raster.setToolTip(tr("TOOLTIP_STREAM_COG"))

    def zoom_to_selected_feature(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        feature = self.current_features[row]
        FootprintManager.highlight_and_zoom(feature, self.iface, zoom=True)

    def load_thumbnail_preview(self, thumbnail_url: str):
        self.lbl_thumbnail.setPixmap(QPixmap())
        if not thumbnail_url:
            self.lbl_thumbnail.setText(tr("PREVIEW_UNAVAILABLE"))
            return

        self.lbl_thumbnail.setText(tr("PREVIEW_LOADING"))

        def worker():
            signed = SignerClient.get_signed_url(thumbnail_url)
            return self.stac_client.fetch_binary(signed)

        def on_done(raw_bytes, exception):
            if exception or not raw_bytes:
                self.lbl_thumbnail.setText(tr("PREVIEW_ERROR"))
                return
            img = QImage.fromData(raw_bytes)
            if img.isNull():
                self.lbl_thumbnail.setText("<i>Formato immagine anteprima non supportato</i>")
                return
            pixmap = QPixmap.fromImage(img).scaled(
                max(220, self.lbl_thumbnail.width() - 12),
                135,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.lbl_thumbnail.setPixmap(pixmap)

        task = AsyncWorkerTask("Download Anteprima STAC", worker, on_done)
        self._submit_task(task)

    def _get_current_asset_info(self):
        asset_data = self.cmb_assets.currentData()
        if not asset_data:
            return None, None, None
        href = asset_data.get("href", "")
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None, None, None
        item_id = self.current_features[selected_rows[0].row()].get("id", "Layer_Raster")
        asset_key = self.cmb_assets.currentText().split(" ")[0]
        layer_title = f"{item_id}_{asset_key}"
        return href, layer_title, asset_data

    def load_selected_asset_streaming(self):
        href, layer_title, _ = self._get_current_asset_info()
        if not href:
            QMessageBox.warning(self, "Errore Asset", "L'asset selezionato non contiene un URL valido.")
            return

        self.btn_load_raster.setEnabled(False)
        self.btn_load_raster.setText(tr("BTN_STREAM_COG_LOADING"))

        def sign_worker():
            return SignerClient.get_signed_url(href)

        def on_signed(signed_url, exception):
            self.btn_load_raster.setEnabled(True)
            self.btn_load_raster.setText(tr("BTN_STREAM_COG"))
            if exception or not signed_url:
                QMessageBox.critical(self, "Errore Firma/Caricamento", f"Impossibile risolvere l'asset:\n{str(exception)}")
                return

            success = RasterLoader.load_cog_streaming(signed_url, layer_title)
            if not success:
                vsi_path = RasterLoader.normalize_vsi_path(signed_url)
                QMessageBox.critical(
                    self,
                    "Errore Caricamento",
                    f"Impossibile caricare il raster remoto in QGIS:\n{vsi_path}\n\n"
                    "Verifica la connettività di rete o che il provider dati consenta l'accesso anonimo/pubblico a questo asset."
                )

        task = AsyncWorkerTask("Firma URL Asset IRIDE", sign_worker, on_signed)
        self._submit_task(task)

    def download_selected_asset_local(self):
        href, layer_title, asset_data = self._get_current_asset_info()
        if not href:
            QMessageBox.warning(self, "Errore Asset", "L'asset selezionato non contiene un URL valido.")
            return

        ext = ".tif"
        if "jp2" in asset_data.get("type", "") or href.endswith(".jp2"):
            ext = ".jp2"
        elif "jpeg" in asset_data.get("type", "") or href.endswith((".jpg", ".jpeg")):
            ext = ".jpg"
        elif href.endswith(".png"):
            ext = ".png"

        default_filename = f"{layer_title}{ext}"
        dest_filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Asset su Disco",
            default_filename,
            "Immagini Raster (*.tif *.tiff *.jp2 *.jpg *.png);;Tutti i file (*.*)"
        )
        if not dest_filepath:
            return

        self.btn_download_raster.setEnabled(False)
        self.progress_download.setValue(0)
        self.progress_download.setVisible(True)

        def download_runner(progress_cb):
            signed_url = SignerClient.get_signed_url(href)
            return self.stac_client.download_asset_to_file(signed_url, dest_filepath, progress_callback=progress_cb)

        def on_download_done(saved_path, exception):
            self.btn_download_raster.setEnabled(True)
            self.progress_download.setVisible(False)
            if exception:
                QMessageBox.critical(self, "Errore Download", f"Download non completato:\n{str(exception)}")
                return

            reply = QMessageBox.question(
                self,
                "Download Completato",
                f"Asset salvato con successo in:\n{saved_path}\n\nVuoi aggiungerlo alla mappa del progetto corrente?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                RasterLoader.load_local_raster(saved_path, layer_title)

        task = DownloadAssetTask(f"Download {layer_title}", download_runner, on_download_done)
        self._submit_task(task)
