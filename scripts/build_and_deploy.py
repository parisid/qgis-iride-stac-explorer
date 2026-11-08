# -*- coding: utf-8 -*-
"""
Script di supporto per il packaging (.zip) e il deploy locale del plugin QGIS 'iride_stac_explorer'.

Utilizzo:
  python scripts/build_and_deploy.py              # Crea dist/iride_stac_explorer.zip
  python scripts/build_and_deploy.py --deploy     # Crea lo .zip e copia il plugin nel profilo QGIS locale
  python scripts/build_and_deploy.py --profile default
"""
import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path

PLUGIN_NAME = "iride_stac_explorer"
ROOT_DIR = Path(__file__).resolve().parent.parent
PLUGIN_SRC_DIR = ROOT_DIR / PLUGIN_NAME
DIST_DIR = ROOT_DIR / "dist"

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".bak"}


def build_zip() -> Path:
    if not PLUGIN_SRC_DIR.is_dir():
        raise FileNotFoundError(f"Directory sorgente del plugin non trovata: {PLUGIN_SRC_DIR}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / f"{PLUGIN_NAME}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PLUGIN_SRC_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if Path(file).suffix in EXCLUDE_EXTS:
                    continue
                abs_file = Path(root) / file
                rel_file = abs_file.relative_to(ROOT_DIR)
                zf.write(abs_file, rel_file.as_posix())

    print(f"[OK] Pacchetto ZIP generato: {zip_path} ({zip_path.stat().st_size} bytes)")
    return zip_path


def get_qgis_plugins_dir(profile: str = "default") -> Path:
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise EnvironmentError("Variabile d'ambiente APPDATA non definita.")
        base = Path(appdata) / "QGIS" / "QGIS3" / "profiles"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "QGIS" / "QGIS3" / "profiles"
    else:
        base = Path.home() / ".local" / "share" / "QGIS" / "QGIS3" / "profiles"

    return base / profile / "python" / "plugins"


def deploy_to_qgis(profile: str = "default") -> Path:
    plugins_dir = get_qgis_plugins_dir(profile)
    target_dir = plugins_dir / PLUGIN_NAME

    plugins_dir.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        shutil.rmtree(target_dir)

    def _ignore(directory, contents):
        ignored = []
        for item in contents:
            if item in EXCLUDE_DIRS or Path(item).suffix in EXCLUDE_EXTS:
                ignored.append(item)
        return ignored

    shutil.copytree(PLUGIN_SRC_DIR, target_dir, ignore=_ignore)
    print(f"[OK] Plugin installato nella cartella del profilo QGIS '{profile}': {target_dir}")
    return target_dir


def main():
    parser = argparse.ArgumentParser(description="Build & Deploy tool per IRIDE STAC Explorer QGIS Plugin.")
    parser.add_argument("--deploy", action="store_true", help="Copia il plugin nella cartella plugins del profilo QGIS locale.")
    parser.add_argument("--profile", default="default", help="Nome del profilo QGIS (default: 'default').")
    args = parser.parse_args()

    build_zip()
    if args.deploy:
        deploy_to_qgis(args.profile)


if __name__ == "__main__":
    main()

