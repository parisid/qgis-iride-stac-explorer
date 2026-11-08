# -*- coding: utf-8 -*-
"""
Modulo di internazionalizzazione (i18n) per IRIDE STAC Explorer.
Fornisce traduzioni automatiche IT/EN in base alla lingua impostata nell'interfaccia di QGIS.
"""
from qgis.core import QgsSettings

TRANSLATIONS = {
    # Plugin & Top Bar
    "PLUGIN_NAME": {
        "it": "IRIDE STAC Explorer",
        "en": "IRIDE STAC Explorer"
    },
    "PLUGIN_TOOLTIP": {
        "it": "Esplora e visualizza prodotti satellitari IRIDE",
        "en": "Explore and stream IRIDE satellite products"
    },
    "BTN_SETTINGS": {
        "it": "⚙ Configura Credenziali / Endpoint",
        "en": "⚙ Configure Credentials / Endpoints"
    },
    "STATUS_TEST": {
        "it": "[TEST: Earth Search]",
        "en": "[TEST: Earth Search]"
    },
    "STATUS_IRIDE_OK": {
        "it": "[IRIDE PROD: API Key OK]",
        "en": "[IRIDE PROD: API Key OK]"
    },
    "STATUS_IRIDE_NO_KEY": {
        "it": "[IRIDE PROD: Manca API Key]",
        "en": "[IRIDE PROD: Missing API Key]"
    },

    # Filters
    "LBL_COLLECTION": {
        "it": "Collezione:",
        "en": "Collection:"
    },
    "ALL_COLLECTIONS": {
        "it": "Tutte le collezioni",
        "en": "All collections"
    },
    "TOOLTIP_REFRESH_COLLECTIONS": {
        "it": "Aggiorna elenco collezioni dal catalogo STAC",
        "en": "Refresh collections list from STAC catalog"
    },
    "CHK_CANVAS_EXTENT": {
        "it": "Usa estensione visualizzata sulla mappa (Canvas BBOX)",
        "en": "Use current map canvas extent (BBOX)"
    },
    "LBL_DATE_FROM": {
        "it": "Dal:",
        "en": "From:"
    },
    "LBL_DATE_TO": {
        "it": "Al:",
        "en": "To:"
    },
    "CHK_CLOUD_COVER": {
        "it": "Nubi Max (%):",
        "en": "Max Cloud (%):"
    },
    "LBL_LIMIT": {
        "it": "Limite:",
        "en": "Limit:"
    },
    "CHK_SHOW_FOOTPRINTS": {
        "it": "Mostra footprint su mappa",
        "en": "Show footprints on map"
    },
    "BTN_ZOOM_FOOTPRINT": {
        "it": "🎯 Zoom a selezionato",
        "en": "🎯 Zoom to selected"
    },
    "BTN_SEARCH": {
        "it": "🔍 Cerca Prodotti Satellitari",
        "en": "🔍 Search Satellite Products"
    },
    "SEARCHING": {
        "it": "Ricerca in corso...",
        "en": "Searching products..."
    },
    "BTN_LOAD_MORE": {
        "it": "⬇ Carica altri risultati (Paginazione)",
        "en": "⬇ Load more results (Pagination)"
    },
    "LOADING_MORE": {
        "it": "Caricamento altri risultati...",
        "en": "Loading more results..."
    },

    # Results Table Headers
    "COL_ID": {
        "it": "ID Prodotto",
        "en": "Product ID"
    },
    "COL_DATETIME": {
        "it": "Data Acquisizione",
        "en": "Acquisition Date"
    },
    "COL_CLOUD": {
        "it": "Copertura Nubi",
        "en": "Cloud Cover"
    },
    "COL_LEVEL": {
        "it": "Livello",
        "en": "Level"
    },

    # Preview & Assets
    "GRP_PREVIEW": {
        "it": "Anteprima Quicklook / Thumbnail",
        "en": "Quicklook / Thumbnail Preview"
    },
    "PREVIEW_SELECT_ITEM": {
        "it": "<i>Seleziona un prodotto per visualizzare l'anteprima</i>",
        "en": "<i>Select a product to view preview</i>"
    },
    "PREVIEW_LOADING": {
        "it": "<i>Caricamento anteprima...</i>",
        "en": "<i>Loading preview...</i>"
    },
    "PREVIEW_UNAVAILABLE": {
        "it": "<i>Nessuna thumbnail disponibile per questo prodotto</i>",
        "en": "<i>No thumbnail available for this product</i>"
    },
    "PREVIEW_ERROR": {
        "it": "<i>Anteprima non disponibile o errore di rete</i>",
        "en": "<i>Preview unavailable or network error</i>"
    },
    "LBL_ASSET": {
        "it": "Asset:",
        "en": "Asset:"
    },
    "BTN_STREAM_COG": {
        "it": "➕ Aggiungi a Layer (Stream Raster)",
        "en": "➕ Add to Layers (Stream Raster)"
    },
    "BTN_STREAM_COG_LOADING": {
        "it": "Firma e streaming raster...",
        "en": "Signing & streaming raster..."
    },
    "TOOLTIP_STREAM_COG": {
        "it": "Carica il raster remoto (GeoTIFF COG, JPEG2000, ecc.) direttamente nel pannello Layer di QGIS via streaming",
        "en": "Loads the remote raster (GeoTIFF COG, JPEG2000, etc.) directly into QGIS Layers panel via streaming"
    },
    "BTN_DOWNLOAD_LOCAL": {
        "it": "💾 Scarica File Locale...",
        "en": "💾 Download Local File..."
    },
    "TOOLTIP_DOWNLOAD_LOCAL": {
        "it": "Scarica l'asset sul disco locale",
        "en": "Downloads the asset to local disk"
    },
    "DISCLAIMER_SHORT": {
        "it": "<small><i>Progetto open-source indipendente. Non affiliato a IRIDE / ESA / ASI. L'uso dei dati è soggetto alle rispettive licenze.</i></small>",
        "en": "<small><i>Independent open-source project. Not affiliated with IRIDE / ESA / ASI. Data usage is subject to provider licenses.</i></small>"
    },

    # Settings Dialog
    "SETTINGS_TITLE": {
        "it": "Configurazione IRIDE STAC Explorer",
        "en": "IRIDE STAC Explorer Configuration"
    },
    "TAB_CONFIG": {
        "it": "Impostazioni & Endpoint",
        "en": "Settings & Endpoints"
    },
    "TAB_ABOUT": {
        "it": "About / Licenza",
        "en": "About / License"
    },
    "GRP_ENDPOINT_SELECT": {
        "it": "Selezione Endpoint STAC",
        "en": "STAC Endpoint Selection"
    },
    "RB_IRIDE": {
        "it": "PRODUCTION - IRIDE online services",
        "en": "PRODUCTION - IRIDE online services"
    },
    "RB_EARTHSEARCH": {
        "it": "TEST - open catalog EARTH (Element84)",
        "en": "TEST - open catalog EARTH (Element84)"
    },
    "GRP_CREDENTIALS": {
        "it": "Autenticazione API IRIDE",
        "en": "IRIDE API Authentication"
    },
    "LBL_API_KEY_IRIDE": {
        "it": "<b>API Key obbligatoria per produzione IRIDE</b> (header 'x-api-key'):",
        "en": "<b>API Key required for IRIDE production</b> (header 'x-api-key'):"
    },
    "LBL_API_KEY_EARTH": {
        "it": "API Key non richiesta per catalogo aperto Element84 Earth Search.",
        "en": "API Key not required for open catalog Element84 Earth Search."
    },
    "GRP_URL_DETAILS": {
        "it": "Dettagli Endpoint dei Servizi",
        "en": "Service Endpoint Details"
    },
    "LBL_DISCOVER_URL": {
        "it": "STAC Discover URL:",
        "en": "STAC Discover URL:"
    },
    "LBL_SIGNER_URL": {
        "it": "Signer Service URL:",
        "en": "Signer Service URL:"
    },
    "LBL_TIMEOUT": {
        "it": "Timeout richieste (secondi):",
        "en": "Request timeout (seconds):"
    },
    "BTN_SAVE": {
        "it": "Salva Configurazione",
        "en": "Save Configuration"
    },
    "BTN_CANCEL": {
        "it": "Annulla",
        "en": "Cancel"
    },

    # About / Info Tab
    "ABOUT_DESC": {
        "it": "Lo scopo del plugin è supportare ricercatori ed amministrazioni pubbliche che hanno accesso ad IRIDE, rendendo immediatamente fruibili e visualizzabili in QGIS i dati e i prodotti della costellazione tramite standard OGC STAC API e streaming raster (GeoTIFF COG, JPEG2000, ecc.) via virtual file system GDAL senza necessità di download integrale preventivo.",
        "en": "The goal of this plugin is to support researchers and public administrations with authorized access to IRIDE, enabling immediate discovery and streaming of constellation data in QGIS through OGC STAC API standards and remote raster streaming (GeoTIFF COG, JPEG2000, etc.) via GDAL virtual file system without requiring full local downloads."
    },
    "ABOUT_COMMUNITY": {
        "it": "Tutti i contributi allo sviluppo, suggerimenti e richieste di implementazione da parte di ricercatori, tecnici della PA e utenti qualificati sono benvenuti e possono essere inoltrati tramite email o aprendo una Issue sul repository GitHub.",
        "en": "Contributions to development, feedback, and feature requests from researchers, public administration specialists, and qualified users are welcome and can be submitted via email or by opening an Issue on GitHub."
    },
    "ABOUT_CREATOR": {
        "it": "Sviluppato da",
        "en": "Developed by"
    },
    "ABOUT_WEBSITE": {
        "it": "Sito Web",
        "en": "Website"
    },
    "ABOUT_REPOSITORY": {
        "it": "Codice Sorgente & Feedback",
        "en": "Source Code & Feedback"
    },
    "ABOUT_LICENSE": {
        "it": "Licenza",
        "en": "License"
    }
}


def get_current_language() -> str:
    """Restituisce 'it' se QGIS è impostato in italiano, altrimenti 'en' per tutte le altre lingue."""
    try:
        qgis_locale = QgsSettings().value("locale/userLocale", "", type=str)
        if qgis_locale and qgis_locale.lower().startswith("it"):
            return "it"
    except Exception:
        pass
    return "en"


def tr(key: str) -> str:
    """Restituisce la traduzione per la chiave specificata nella lingua corrente di QGIS."""
    lang = get_current_language()
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))

