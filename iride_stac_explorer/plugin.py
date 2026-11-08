# -*- coding: utf-8 -*-
import os
from .core.qt_compat import QAction, QIcon, Qt
from qgis.gui import QgisInterface
from .gui.dock_widget import IrideDockWidget
from .core.i18n import tr

class IrideStacExplorerPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.dock_widget = None
        self.action = None

    def initGui(self):
        """Costruisce le voci di menu e la action nella toolbar di QGIS."""
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.action = QAction(icon, tr("PLUGIN_NAME"), self.iface.mainWindow())
        self.action.setStatusTip(tr("PLUGIN_TOOLTIP"))
        self.action.triggered.connect(self.toggle_dock)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&IRIDE Explorer", self.action)

    def unload(self):
        """Ripulisce l'interfaccia alla disattivazione o reload del plugin."""
        if self.action:
            self.iface.removePluginMenu("&IRIDE Explorer", self.action)
            self.iface.removeToolBarIcon(self.action)
            del self.action

        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)
            self.dock_widget.deleteLater()
            self.dock_widget = None

    def toggle_dock(self):
        """Apre o porta in primo piano il Dock Widget."""
        if not self.dock_widget:
            self.dock_widget = IrideDockWidget(self.iface, self.iface.mainWindow())
            self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_widget)
        
        self.dock_widget.show()
        self.dock_widget.raise_()
