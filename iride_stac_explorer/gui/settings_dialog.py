# -*- coding: utf-8 -*-
from ..core.qt_compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QGroupBox, QSpinBox,
    QTabWidget, QWidget, QRadioButton, QButtonGroup, QFormLayout
)
from ..core.config import ConfigManager
from ..core.i18n import tr

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("SETTINGS_TITLE"))
        self.resize(600, 560)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab_config = QWidget()
        self.tab_about = QWidget()
        self.tabs.addTab(self.tab_config, tr("TAB_CONFIG"))
        self.tabs.addTab(self.tab_about, tr("TAB_ABOUT"))

        # --- Tab 1: Impostazioni & Endpoint ---
        layout = QVBoxLayout(self.tab_config)

        # Selezione Endpoint / Ambiente
        grp_endpoint = QGroupBox(tr("GRP_ENDPOINT_SELECT"))
        lay_endpoint = QVBoxLayout(grp_endpoint)

        self.btn_grp_profile = QButtonGroup(self)
        self.rb_iride = QRadioButton(tr("RB_IRIDE"))
        self.rb_earthsearch = QRadioButton(tr("RB_EARTHSEARCH"))
        self.btn_grp_profile.addButton(self.rb_iride)
        self.btn_grp_profile.addButton(self.rb_earthsearch)

        current_profile = ConfigManager.get_endpoint_profile()
        if current_profile == ConfigManager.PROFILE_EARTH_SEARCH:
            self.rb_earthsearch.setChecked(True)
        else:
            self.rb_iride.setChecked(True)

        self.rb_iride.toggled.connect(self.on_endpoint_changed)
        self.rb_earthsearch.toggled.connect(self.on_endpoint_changed)

        lay_endpoint.addWidget(self.rb_iride)
        lay_endpoint.addWidget(self.rb_earthsearch)
        layout.addWidget(grp_endpoint)

        # Autenticazione API IRIDE
        self.grp_cred = QGroupBox(tr("GRP_CREDENTIALS"))
        lay_cred = QVBoxLayout(self.grp_cred)
        self.lbl_api_key_hint = QLabel()
        lay_cred.addWidget(self.lbl_api_key_hint)
        self.txt_api_key = QLineEdit(ConfigManager.get_api_key())
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("IRIDE API Key")
        lay_cred.addWidget(self.txt_api_key)
        layout.addWidget(self.grp_cred)

        # Dettagli URL Endpoint
        grp_urls = QGroupBox(tr("GRP_URL_DETAILS"))
        lay_urls = QVBoxLayout(grp_urls)
        lay_urls.addWidget(QLabel(tr("LBL_DISCOVER_URL")))
        self.txt_discover = QLineEdit(ConfigManager.get_discover_url())
        lay_urls.addWidget(self.txt_discover)
        
        self.lbl_sign_url = QLabel(tr("LBL_SIGNER_URL"))
        lay_urls.addWidget(self.lbl_sign_url)
        self.txt_sign = QLineEdit(ConfigManager.get_sign_url())
        lay_urls.addWidget(self.txt_sign)

        h_to = QHBoxLayout()
        h_to.addWidget(QLabel(tr("LBL_TIMEOUT")))
        self.spn_timeout = QSpinBox()
        self.spn_timeout.setRange(5, 120)
        self.spn_timeout.setValue(ConfigManager.get_timeout())
        h_to.addWidget(self.spn_timeout)
        lay_urls.addLayout(h_to)
        layout.addWidget(grp_urls)

        layout.addStretch()

        # Aggiorna lo stato dei campi in base alla selezione iniziale
        self.update_fields_for_profile()

        # --- Tab 2: About / Licenza ---
        about_layout = QVBoxLayout(self.tab_about)
        
        # Info Progetto e Autore
        grp_author = QGroupBox(tr("TAB_ABOUT"))
        author_layout = QFormLayout(grp_author)
        author_layout.addRow(QLabel("<b>IRIDE STAC Explorer (QGIS Plugin)</b>"))
        
        lbl_desc = QLabel(tr("ABOUT_DESC"))
        lbl_desc.setWordWrap(True)
        author_layout.addRow(lbl_desc)

        lbl_community = QLabel(f"<i>{tr('ABOUT_COMMUNITY')}</i>")
        lbl_community.setWordWrap(True)
        lbl_community.setStyleSheet("color: #495057;")
        author_layout.addRow(lbl_community)

        lbl_creator = QLabel("Davide Parisi (<a href='mailto:dp@davideparisi.com'>dp@davideparisi.com</a>)")
        lbl_creator.setOpenExternalLinks(True)
        author_layout.addRow(f"<b>{tr('ABOUT_CREATOR')}:</b>", lbl_creator)
        
        lbl_site = QLabel("<a href='https://www.davideparisi.com'>https://www.davideparisi.com</a>")
        lbl_site.setOpenExternalLinks(True)
        author_layout.addRow(f"<b>{tr('ABOUT_WEBSITE')}:</b>", lbl_site)

        lbl_repo = QLabel("<a href='https://github.com/parisid/qgis-iride-stac-explorer'>github.com/parisid/qgis-iride-stac-explorer</a>")
        lbl_repo.setOpenExternalLinks(True)
        author_layout.addRow(f"<b>{tr('ABOUT_REPOSITORY')}:</b>", lbl_repo)
        
        author_layout.addRow(f"<b>{tr('ABOUT_LICENSE')}:</b>", QLabel("MIT License (Open Source)"))
        about_layout.addWidget(grp_author)

        # Disclaimer Ufficiale Vincolante
        about_layout.addWidget(QLabel("<b>Important Notice &amp; Disclaimer:</b>"))
        txt_disc = QTextEdit()
        txt_disc.setReadOnly(True)
        txt_disc.setPlainText(ConfigManager.OFFICIAL_DISCLAIMER)
        about_layout.addWidget(txt_disc)

        main_layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton(tr("BTN_SAVE"))
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton(tr("BTN_CANCEL"))
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def on_endpoint_changed(self):
        if self.rb_earthsearch.isChecked():
            self.txt_discover.setText(ConfigManager.EARTH_SEARCH_DISCOVER_URL)
            self.txt_sign.setText("")
        else:
            self.txt_discover.setText(ConfigManager.DEFAULT_DISCOVER_URL)
            self.txt_sign.setText(ConfigManager.DEFAULT_SIGN_URL)
        self.update_fields_for_profile()

    def update_fields_for_profile(self):
        is_iride = self.rb_iride.isChecked()
        if is_iride:
            self.grp_cred.setEnabled(True)
            self.lbl_api_key_hint.setText(tr("LBL_API_KEY_IRIDE"))
            self.lbl_sign_url.setVisible(True)
            self.txt_sign.setVisible(True)
        else:
            self.grp_cred.setEnabled(False)
            self.lbl_api_key_hint.setText(tr("LBL_API_KEY_EARTH"))
            self.lbl_sign_url.setVisible(False)
            self.txt_sign.setVisible(False)

    def save_settings(self):
        profile = ConfigManager.PROFILE_EARTH_SEARCH if self.rb_earthsearch.isChecked() else ConfigManager.PROFILE_IRIDE_PRODUCTION
        ConfigManager.set_endpoint_profile(profile)
        ConfigManager.set_api_key(self.txt_api_key.text())
        ConfigManager.set_discover_url(self.txt_discover.text())
        ConfigManager.set_sign_url(self.txt_sign.text())
        ConfigManager.set_timeout(self.spn_timeout.value())
        self.accept()
