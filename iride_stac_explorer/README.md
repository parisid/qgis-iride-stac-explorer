# IRIDE STAC Explorer (QGIS Plugin)

Independent QGIS plugin to query, filter, and stream Earth Observation products from the **IRIDE** constellation and STAC-compliant catalogs directly into QGIS using Cloud Optimized GeoTIFF (COG) via `/vsicurl/`.

## Important Notice & Disclaimer
> **This plugin is an independent, third-party open-source project and is NOT officially affiliated with, endorsed by, maintained, or sponsored by the IRIDE programme, the European Space Agency (ESA), the Italian Space Agency (ASI), or the IRIDE Marketplace. Its sole purpose is to provide a desktop bridge to facilitate the discovery and visualization of data within QGIS.**
> 
> **Access to and use of IRIDE satellite data, products, and services are strictly governed by their respective terms of service, end-user licensing agreements (EULA), and usage policies established by the data providers and platform authorities. Users are solely responsible for obtaining their own valid API credentials, ensuring their compliance with applicable data quotas and access rights, and verifying that their data usage complies with all relevant legal and contractual frameworks.**

## Features
- **STAC API 1.0.0 Search**: Query by spatial extent (canvas BBOX) and datetime ranges.
- **Asynchronous Execution**: Queries run on background `QgsTask` workers to prevent GUI freezing.
- **Direct COG Streaming**: Loads imagery directly using GDAL `/vsicurl/` without full local downloads.
- **Offline / Mock Mode**: Full local development and testing mode without needing active IRIDE credentials.
- **Secure Configuration**: Stores API key and custom endpoints via `QgsSettings`.
