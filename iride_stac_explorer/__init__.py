# -*- coding: utf-8 -*-
"""
Entry-point standard per QGIS.
Inizializza la classe principale del plugin tramite classFactory.
"""

def classFactory(iface):
    """Carica la classe principale del plugin.
    :param iface: Handle all'interfaccia corrente di QGIS (QgisInterface).
    """
    from .plugin import IrideStacExplorerPlugin
    return IrideStacExplorerPlugin(iface)
