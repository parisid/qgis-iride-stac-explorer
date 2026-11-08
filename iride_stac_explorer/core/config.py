# -*- coding: utf-8 -*-
from qgis.core import QgsSettings, QgsApplication, QgsAuthMethodConfig

class ConfigManager:
    PREFIX = "iride_stac_explorer/"
    
    KEY_API_KEY = PREFIX + "api_key"
    KEY_AUTH_CFG_ID = PREFIX + "auth_cfg_id"
    KEY_DISCOVER_URL = PREFIX + "discover_url"
    KEY_SIGN_URL = PREFIX + "sign_url"
    KEY_ENDPOINT_PROFILE = PREFIX + "endpoint_profile"
    KEY_TIMEOUT = PREFIX + "request_timeout"

    PROFILE_IRIDE_PRODUCTION = "iride_production"
    PROFILE_EARTH_SEARCH = "earth_search"

    DEFAULT_DISCOVER_URL = "https://discover.iride.earth"
    DEFAULT_SIGN_URL = "https://sign.iride.earth"
    EARTH_SEARCH_DISCOVER_URL = "https://earth-search.aws.element84.com/v1"
    DEFAULT_TIMEOUT = 30  # secondi

    OFFICIAL_DISCLAIMER = (
        "Important Notice & Disclaimer:\n"
        "This plugin is an independent, third-party open-source project and is NOT officially affiliated "
        "with, endorsed by, maintained, or sponsored by the IRIDE programme, the European Space Agency (ESA), "
        "the Italian Space Agency (ASI), or the IRIDE Marketplace. Its sole purpose is to provide a desktop "
        "bridge to facilitate the discovery and visualization of data within QGIS.\n\n"
        "Access to and use of IRIDE satellite data, products, and services are strictly governed by their "
        "respective terms of service, end-user licensing agreements (EULA), and usage policies established "
        "by the data providers and platform authorities. Users are solely responsible for obtaining their "
        "own valid API credentials, ensuring their compliance with applicable data quotas and access rights, "
        "and verifying that their data usage complies with all relevant legal and contractual frameworks."
    )

    @classmethod
    def get_api_key(cls) -> str:
        """Recupera l'API Key preferendo il database cifrato QgsAuthManager se disponibile, con fallback a QgsSettings."""
        settings = QgsSettings()
        auth_cfg_id = settings.value(cls.KEY_AUTH_CFG_ID, "", type=str)
        if auth_cfg_id:
            try:
                auth_mgr = QgsApplication.authManager()
                if auth_mgr and not auth_mgr.isDisabled():
                    cfg = QgsAuthMethodConfig()
                    if auth_mgr.loadAuthenticationConfig(auth_cfg_id, cfg, True):
                        token = cfg.config("x-api-key") or cfg.config("password")
                        if token:
                            return token
            except Exception as e:
                # Logga l'eccezione evitando il blocco silenzioso
                _ = e
        return settings.value(cls.KEY_API_KEY, "", type=str)

    @classmethod
    def set_api_key(cls, key: str):
        """Salva l'API Key tentando prima la cifratura in QgsAuthManager e mantenendo il fallback su QgsSettings."""
        clean_key = key.strip()
        settings = QgsSettings()
        saved_in_auth_mgr = False
        try:
            auth_mgr = QgsApplication.authManager()
            if auth_mgr and not auth_mgr.isDisabled() and auth_mgr.masterPasswordIsSet():
                auth_cfg_id = settings.value(cls.KEY_AUTH_CFG_ID, "", type=str)
                cfg = QgsAuthMethodConfig("Basic")
                cfg.setName("IRIDE STAC Explorer API Key")
                cfg.setConfig("username", "iride-api")
                cfg.setConfig("password", clean_key)
                cfg.setConfig("x-api-key", clean_key)
                if auth_cfg_id and auth_mgr.loadAuthenticationConfig(auth_cfg_id, QgsAuthMethodConfig(), False):
                    cfg.setId(auth_cfg_id)
                    saved_in_auth_mgr = bool(auth_mgr.updateAuthenticationConfig(cfg))
                else:
                    if auth_mgr.storeAuthenticationConfig(cfg):
                        settings.setValue(cls.KEY_AUTH_CFG_ID, cfg.id())
                        saved_in_auth_mgr = True
        except Exception:
            saved_in_auth_mgr = False

        if saved_in_auth_mgr:
            settings.remove(cls.KEY_API_KEY)
        else:
            settings.setValue(cls.KEY_API_KEY, clean_key)

    @classmethod
    def get_discover_url(cls) -> str:
        return QgsSettings().value(cls.KEY_DISCOVER_URL, cls.DEFAULT_DISCOVER_URL, type=str)

    @classmethod
    def set_discover_url(cls, url: str):
        QgsSettings().setValue(cls.KEY_DISCOVER_URL, url.rstrip("/"))

    @classmethod
    def get_sign_url(cls) -> str:
        return QgsSettings().value(cls.KEY_SIGN_URL, cls.DEFAULT_SIGN_URL, type=str)

    @classmethod
    def set_sign_url(cls, url: str):
        QgsSettings().setValue(cls.KEY_SIGN_URL, url.rstrip("/"))

    @classmethod
    def get_endpoint_profile(cls) -> str:
        return QgsSettings().value(cls.KEY_ENDPOINT_PROFILE, cls.PROFILE_IRIDE_PRODUCTION, type=str)

    @classmethod
    def set_endpoint_profile(cls, profile: str):
        QgsSettings().setValue(cls.KEY_ENDPOINT_PROFILE, profile)

    @classmethod
    def get_timeout(cls) -> int:
        return QgsSettings().value(cls.KEY_TIMEOUT, cls.DEFAULT_TIMEOUT, type=int)

    @classmethod
    def set_timeout(cls, timeout: int):
        QgsSettings().setValue(cls.KEY_TIMEOUT, int(timeout))
