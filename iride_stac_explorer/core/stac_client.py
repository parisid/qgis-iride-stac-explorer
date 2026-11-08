# -*- coding: utf-8 -*-
import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Callable
from qgis.core import QgsMessageLog, Qgis
from .config import ConfigManager

class StacClient:
    """Client per l'interrogazione dell'endpoint STAC Discovery."""

    def __init__(self):
        self.log_tag = "IRIDE Explorer"

    def search(self, 
               bbox: Optional[List[float]] = None, 
               collections: Optional[List[str]] = None, 
               datetime_range: Optional[str] = None, 
               max_cloud_cover: Optional[float] = None,
               limit: int = 50,
               next_url: Optional[str] = None,
               next_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if next_url:
            endpoint = next_url
            payload = next_body or {}
            method = "POST" if next_body else "GET"
            json_data = json.dumps(payload).encode("utf-8") if next_body else None
        else:
            endpoint = f"{ConfigManager.get_discover_url()}/search"
            method = "POST"
            payload = {"limit": limit}

            if bbox and len(bbox) == 4:
                payload["bbox"] = bbox
            if collections:
                payload["collections"] = collections
            if datetime_range:
                payload["datetime"] = datetime_range
            if max_cloud_cover is not None:
                payload["query"] = {
                    "eo:cloud_cover": {"lte": max_cloud_cover}
                }
            json_data = json.dumps(payload).encode("utf-8")

        if not endpoint.startswith(("http://", "https://")):
            raise ValueError(f"Schema URL non supportato: {endpoint}")

        req = urllib.request.Request(endpoint, data=json_data, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/geo+json")

        api_key = ConfigManager.get_api_key()
        if api_key:
            req.add_header("x-api-key", api_key)

        timeout = ConfigManager.get_timeout()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:  # nosec B310
                if response.status == 200:
                    raw_content = response.read().decode("utf-8")
                    data = json.loads(raw_content)
                    return self._filter_features(data, collections=collections, max_cloud_cover=max_cloud_cover)
                else:
                    raise RuntimeError(f"HTTP Error {response.status}: {response.reason}")
        except urllib.error.HTTPError as e:
            err_msg = f"Errore server STAC [{e.code}]: {e.read().decode('utf-8', errors='ignore')}"
            QgsMessageLog.logMessage(err_msg, self.log_tag, Qgis.Critical)
            raise RuntimeError(err_msg)
        except Exception as e:
            QgsMessageLog.logMessage(f"Eccezione di rete: {str(e)}", self.log_tag, Qgis.Critical)
            raise

    @staticmethod
    def extract_next_link(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Estrae le informazioni sul cursore di paginazione 'next' dai links STAC."""
        links = data.get("links", [])
        for link in links:
            if link.get("rel") == "next":
                return {
                    "href": link.get("href"),
                    "method": link.get("method", "GET").upper(),
                    "body": link.get("body")
                }
        return None

    def download_asset_to_file(self, 
                               url: str, 
                               dest_filepath: str, 
                               progress_callback: Optional[Callable[[float], bool]] = None,
                               chunk_size: int = 65536) -> str:
        """Scarica un asset binario su disco a blocchi notificando il progresso. Ritorna il percorso del file salvato."""
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Schema URL non supportato per il download: {url}")

        req = urllib.request.Request(url, method="GET")
        api_key = ConfigManager.get_api_key()
        if api_key and ("iride.earth" in url or url.startswith("iride://")):
            req.add_header("x-api-key", api_key)

        timeout = ConfigManager.get_timeout()
        with urllib.request.urlopen(req, timeout=timeout) as response:  # nosec B310
            total_size = response.headers.get("Content-Length")
            total_bytes = int(total_size) if total_size and total_size.isdigit() else 0

            downloaded = 0
            with open(dest_filepath, "wb") as out_file:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_bytes > 0:
                        pct = (downloaded / total_bytes) * 100.0
                        should_continue = progress_callback(min(100.0, pct))
                        if should_continue is False:
                            raise InterruptedError("Download annullato dall'utente.")
        return dest_filepath

    @staticmethod
    def _filter_features(data: Dict[str, Any],
                         collections: Optional[List[str]] = None,
                         max_cloud_cover: Optional[float] = None) -> Dict[str, Any]:
        features = data.get("features", [])
        filtered = []
        for feat in features:
            if collections and feat.get("collection") not in collections:
                continue
            if max_cloud_cover is not None:
                props = feat.get("properties", {})
                cc = props.get("eo:cloud_cover")
                if cc is not None:
                    try:
                        if float(cc) > float(max_cloud_cover):
                            continue
                    except (ValueError, TypeError):
                        pass
            filtered.append(feat)
        result = dict(data)
        result["features"] = filtered
        return result

    def fetch_binary(self, url: str) -> bytes:
        fetch_url = url
        if fetch_url.startswith("s3://"):
            bucket_and_key = fetch_url[5:]
            parts = bucket_and_key.split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            fetch_url = f"https://{bucket}.s3.amazonaws.com/{key}"

        if not fetch_url.startswith(("http://", "https://")):
            raise ValueError(f"Schema URL non supportato per la risorsa binaria: {fetch_url}")

        req = urllib.request.Request(fetch_url, method="GET")
        api_key = ConfigManager.get_api_key()
        if api_key and ("iride.earth" in fetch_url or fetch_url.startswith("iride://")):
            req.add_header("x-api-key", api_key)
        with urllib.request.urlopen(req, timeout=ConfigManager.get_timeout()) as response:  # nosec B310
            return response.read()

    def get_collections(self) -> List[Dict[str, Any]]:
        endpoint = f"{ConfigManager.get_discover_url()}/collections"
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError(f"Schema URL non supportato per collections: {endpoint}")

        req = urllib.request.Request(endpoint, method="GET")
        req.add_header("Accept", "application/json")
        api_key = ConfigManager.get_api_key()
        if api_key:
            req.add_header("x-api-key", api_key)

        with urllib.request.urlopen(req, timeout=ConfigManager.get_timeout()) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
            return data.get("collections", [])

    def _load_mock_search(self) -> Dict[str, Any]:
        mock_path = os.path.join(os.path.dirname(__file__), "..", "mock_data", "sample_search_response.json")
        if not os.path.exists(mock_path):
            raise FileNotFoundError(f"Mock file non trovato: {mock_path}")
        with open(mock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_mock_collections(self) -> List[Dict[str, Any]]:
        mock_path = os.path.join(os.path.dirname(__file__), "..", "mock_data", "sample_collections.json")
        if not os.path.exists(mock_path):
            return [{"id": "IRIDE-OPT-L2A", "title": "Ottico Multispettrale L2A (Mock)"}]
        with open(mock_path, "r", encoding="utf-8") as f:
            return json.load(f).get("collections", [])
