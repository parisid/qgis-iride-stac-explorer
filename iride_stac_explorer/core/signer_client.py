# -*- coding: utf-8 -*-
import json
import urllib.request
from .config import ConfigManager

class SignerClient:
    """Interagisce con il servizio di firma di IRIDE per ottenere i signed URL dei COG."""

    @staticmethod
    def get_signed_url(asset_href: str) -> str:
        if not asset_href.startswith("iride://") and "iride.earth" not in asset_href:
            return asset_href

        endpoint = f"{ConfigManager.get_sign_url()}/sign"
        payload = json.dumps({"asset_url": asset_href}).encode("utf-8")
        req = urllib.request.Request(endpoint, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        
        api_key = ConfigManager.get_api_key()
        if api_key:
            req.add_header("x-api-key", api_key)

        with urllib.request.urlopen(req, timeout=ConfigManager.get_timeout()) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("signed_url", asset_href)
