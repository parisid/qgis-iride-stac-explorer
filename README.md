# IRIDE STAC Explorer (QGIS Plugin)

[![QGIS Version](https://img.shields.io/badge/QGIS-3.28%2B-589632.svg)](https://qgis.org)
[![STAC API](https://img.shields.io/badge/STAC%20API-1.0.0-blue.svg)](https://stacspec.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An independent, open-source QGIS plugin to query, filter, and stream Earth Observation products from the **IRIDE** constellation and STAC-compliant catalogs directly into QGIS via GDAL streaming protocols (`/vsicurl/`, `/vsis3/`) without requiring full local data downloads.

Developed by **[Davide Parisi](https://www.davideparisi.com)** to support researchers, remote sensing specialists, and public administrations in making IRIDE constellation data immediately accessible on desktop GIS environments.

---

## Important Notice & Disclaimer

> **This plugin is an independent, third-party open-source project and is NOT officially affiliated with, endorsed by, maintained, or sponsored by the IRIDE programme, the European Space Agency (ESA), the Italian Space Agency (ASI), or the IRIDE Marketplace. Its sole purpose is to provide a desktop bridge to facilitate the discovery and visualization of data within QGIS.**
> 
> **Access to and use of IRIDE satellite data, products, and services are strictly governed by their respective terms of service, end-user licensing agreements (EULA), and usage policies established by the data providers and platform authorities. Users are solely responsible for obtaining their own valid API credentials, ensuring their compliance with applicable data quotas and access rights, and verifying that their data usage complies with all relevant legal and contractual frameworks.**

---

## Key Features

- **OGC STAC API 1.0.0 Compliance:** Search across IRIDE products and open catalogs using spatial extents (current map canvas BBOX) and temporal filters.
- **Pure Asynchronous Architecture:** All queries, collections fetching, asset signing, and thumbnail downloads run in background `QgsTask` workers to prevent GUI freezing.
- **Universal Remote Raster Streaming:** Direct streaming into QGIS Layers for Cloud Optimized GeoTIFF (COG), JPEG2000, and other GDAL-supported formats via `/vsicurl/`.
- **Smart Asset Selection:** Automatically identifies and pre-selects primary visual and data bands (RGB True Color, SAR VV/VH polarizations, DEM elevation).
- **Interactive Footprints:** Automatically renders and highlights query result bounding footprints on the map canvas.
- **Thumbnail Quicklooks:** Live visual previews of satellite scenes directly inside the dock panel.
- **Dual Endpoint Environment:** 
  - `PRODUCTION - IRIDE online services` (requires API Key via `x-api-key` header)
  - `TEST - open catalog EARTH (Element84)` (public open catalog for immediate testing)
- **Bilingual Support (i18n):** Native Italian and English interface, automatically matching QGIS user locale.

---

## Screenshots

| Satellite Footprints & Raster Streaming | Quicklook Previews & Asset Selection |
| :---: | :---: |
| ![Footprints and Map](images/Screenshot%202026-11-08%20161853.png) | ![Preview and Filters](images/Screenshot%202026-11-08%20161042.png) |

---

## Installation

### From QGIS Official Plugin Repository (Recommended)
1. Open QGIS (`3.28` or newer).
2. Go to **Plugins** -> **Manage and Install Plugins...**
3. In the Settings tab, ensure *"Show also experimental plugins"* is checked.
4. Search for **IRIDE STAC Explorer** and click **Install Plugin**.

### Manual Installation from ZIP
1. Download the latest `iride_stac_explorer.zip` from [Releases](https://github.com/parisid/qgis-iride-stac-explorer/releases).
2. In QGIS, navigate to **Plugins** -> **Manage and Install Plugins...** -> **Install from ZIP**.
3. Select the `.zip` file and click **Install Plugin**.

---

## Configuration & Usage

1. Open the plugin from the toolbar icon or the menu **IRIDE Explorer** -> **IRIDE STAC Explorer**.
2. Click **⚙ Configure Credentials / Endpoints**:
   - Choose **PRODUCTION - IRIDE online services** and input your IRIDE API Key.
   - Or choose **TEST - open catalog EARTH** to test functionality immediately without credentials.
3. Pan/zoom the map canvas over your area of interest, select a collection and date range, and click **🔍 Search Satellite Products**.
4. Browse the results table, view the quicklook preview, and click **➕ Add to Layers (Stream Raster)** to stream imagery directly onto your map.

---

## Community & Contributions

Contributions, feedback, and feature requests from researchers, public administration specialists, and GIS professionals are warmly welcome!

- **Issue Tracker:** [GitHub Issues](https://github.com/parisid/qgis-iride-stac-explorer/issues)
- **Author & Contact:** Davide Parisi ([dp@davideparisi.com](mailto:dp@davideparisi.com))
- **Website:** [https://www.davideparisi.com](https://www.davideparisi.com)

---

## License

This project is released under the **MIT License**. See [LICENSE](iride_stac_explorer/LICENSE) for details.
