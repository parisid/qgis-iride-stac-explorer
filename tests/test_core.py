# -*- coding: utf-8 -*-
"""
Suite di test unitari per verificare la logica core, i filtri STAC, la firma URL,
e la conformità del manifesto e dei disclaimer anche in assenza di un'istanza grafica QGIS attiva.

Esecuzione:
  python -m unittest discover -s tests -v
"""
import configparser
import sys
import types
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _install_qgis_stubs_if_needed():
    """Installa stub leggeri per qgis.core, qgis.gui e PyQt5 se eseguito fuori dall'ambiente Python di QGIS."""
    try:
        import qgis.core  # noqa: F401
        return
    except ImportError:
        pass

    store = {}

    class DummySettings:
        def value(self, key, default=None, type=None):
            val = store.get(key, default)
            if type is not None and val is not None:
                if type is bool and isinstance(val, str):
                    return val.lower() in ("true", "1", "yes")
                return type(val)
            return val

        def setValue(self, key, value):
            store[key] = value

        def remove(self, key):
            store.pop(key, None)

    class DummyQgsTask:
        CanCancel = 1

        def __init__(self, description="", flags=0):
            self.description = description
            self.flags = flags
            self._canceled = False

        def isCanceled(self):
            return self._canceled

    class DummyQgis:
        Critical = 2
        Warning = 1
        Info = 0

    class DummyMessageLog:
        @staticmethod
        def logMessage(msg, tag="", level=0):
            pass

    class DummyApplication:
        @staticmethod
        def authManager():
            return None

    class DummyAuthMethodConfig:
        def __init__(self, method=""):
            self.method = method

    qgis_mod = types.ModuleType("qgis")
    qgis_core = types.ModuleType("qgis.core")
    qgis_gui = types.ModuleType("qgis.gui")
    qgis_pyqt = types.ModuleType("qgis.PyQt")
    qgis_pyqt_core = types.ModuleType("qgis.PyQt.QtCore")
    qgis_pyqt_gui = types.ModuleType("qgis.PyQt.QtGui")
    qgis_pyqt_widgets = types.ModuleType("qgis.PyQt.QtWidgets")

    qgis_pyqt_core.Qt = types.SimpleNamespace()
    qgis_pyqt_core.QDate = types.SimpleNamespace()
    qgis_pyqt_core.QVariant = types.SimpleNamespace()
    qgis_pyqt_gui.QIcon = object
    qgis_pyqt_gui.QPixmap = object
    qgis_pyqt_gui.QImage = object
    qgis_pyqt_gui.QColor = object
    for w in [
        "QAction", "QDockWidget", "QWidget", "QVBoxLayout", "QHBoxLayout",
        "QPushButton", "QLabel", "QLineEdit", "QComboBox", "QDateEdit", "QTableWidget",
        "QTableWidgetItem", "QHeaderView", "QMessageBox", "QCheckBox",
        "QAbstractItemView", "QSpinBox", "QGroupBox", "QFileDialog",
        "QProgressBar", "QDialog", "QTextEdit", "QTabWidget", "QRadioButton",
        "QButtonGroup", "QFormLayout"
    ]:
        setattr(qgis_pyqt_widgets, w, object)

    qgis_pyqt.QtCore = qgis_pyqt_core
    qgis_pyqt.QtGui = qgis_pyqt_gui
    qgis_pyqt.QtWidgets = qgis_pyqt_widgets

    qgis_core.QgsSettings = DummySettings
    qgis_core.QgsTask = DummyQgsTask
    qgis_core.Qgis = DummyQgis
    qgis_core.QgsMessageLog = DummyMessageLog
    qgis_core.QgsApplication = DummyApplication
    qgis_core.QgsAuthMethodConfig = DummyAuthMethodConfig
    qgis_gui.QgisInterface = object

    sys.modules["qgis"] = qgis_mod
    sys.modules["qgis.core"] = qgis_core
    sys.modules["qgis.gui"] = qgis_gui
    sys.modules["qgis.PyQt"] = qgis_pyqt
    sys.modules["qgis.PyQt.QtCore"] = qgis_pyqt_core
    sys.modules["qgis.PyQt.QtGui"] = qgis_pyqt_gui
    sys.modules["qgis.PyQt.QtWidgets"] = qgis_pyqt_widgets


_install_qgis_stubs_if_needed()

from iride_stac_explorer.core.config import ConfigManager  # noqa: E402
from iride_stac_explorer.core.stac_client import StacClient  # noqa: E402
from iride_stac_explorer.core.signer_client import SignerClient  # noqa: E402
from iride_stac_explorer.core.async_tasks import AsyncWorkerTask  # noqa: E402


class TestIridePluginCore(unittest.TestCase):
    def setUp(self):
        ConfigManager.set_endpoint_profile(ConfigManager.PROFILE_IRIDE_PRODUCTION)
        ConfigManager.set_discover_url(ConfigManager.DEFAULT_DISCOVER_URL)
        ConfigManager.set_sign_url(ConfigManager.DEFAULT_SIGN_URL)
        ConfigManager.set_timeout(30)
        ConfigManager.set_api_key("test-secret-key")

    def test_config_persistence(self):
        self.assertEqual(ConfigManager.get_api_key(), "test-secret-key")
        self.assertEqual(ConfigManager.get_discover_url(), "https://discover.iride.earth")
        self.assertEqual(ConfigManager.get_sign_url(), "https://sign.iride.earth")
        self.assertEqual(ConfigManager.get_endpoint_profile(), ConfigManager.PROFILE_IRIDE_PRODUCTION)
        ConfigManager.set_endpoint_profile(ConfigManager.PROFILE_EARTH_SEARCH)
        self.assertEqual(ConfigManager.get_endpoint_profile(), ConfigManager.PROFILE_EARTH_SEARCH)
        self.assertEqual(ConfigManager.get_timeout(), 30)
        ConfigManager.set_timeout(45)
        self.assertEqual(ConfigManager.get_timeout(), 45)

    def test_filter_features_helper(self):
        import json
        mock_file = ROOT_DIR / "iride_stac_explorer" / "mock_data" / "sample_search_response.json"
        data = json.loads(mock_file.read_text(encoding="utf-8"))

        filtered_sar = StacClient._filter_features(data, collections=["IRIDE-SAR-L1C"])
        self.assertEqual(len(filtered_sar["features"]), 1)
        self.assertEqual(filtered_sar["features"][0]["id"], "IRIDE_SAR_L1C_20261102T053012_SAR_001")

        filtered_cloud = StacClient._filter_features(data, collections=["IRIDE-OPT-L2A"], max_cloud_cover=10.0)
        self.assertEqual(len(filtered_cloud["features"]), 1)
        self.assertEqual(filtered_cloud["features"][0]["id"], "IRIDE_OPT_L2A_20261105T101530_CAM_001")

    def test_signer_passthrough_in_external_url(self):
        ext_url = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/test/TCI.tif"
        self.assertEqual(SignerClient.get_signed_url(ext_url), ext_url)

    def test_async_worker_task_execution(self):
        captured = {}

        def worker():
            return {"count": 42}

        def on_done(res, exc):
            captured["res"] = res
            captured["exc"] = exc

        task = AsyncWorkerTask("Test Worker", worker, on_done)
        ok = task.run()
        task.finished(ok)
        self.assertTrue(ok)
        self.assertIsNone(captured["exc"])
        self.assertEqual(captured["res"], {"count": 42})

    def test_metadata_and_disclaimer_compliance(self):
        meta_path = ROOT_DIR / "iride_stac_explorer" / "metadata.txt"
        self.assertTrue(meta_path.exists())
        cp = configparser.ConfigParser()
        cp.read(meta_path, encoding="utf-8")
        self.assertIn("general", cp)
        about_text = cp["general"].get("about", "")
        self.assertIn("NOT officially affiliated with, endorsed by, maintained, or sponsored by the IRIDE programme", about_text)
        self.assertEqual(cp["general"].get("icon"), "resources/icon.png")

        icon_path = ROOT_DIR / "iride_stac_explorer" / "resources" / "icon.png"
        self.assertTrue(icon_path.exists())
        self.assertEqual(icon_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()

