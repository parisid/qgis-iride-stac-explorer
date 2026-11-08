# -*- coding: utf-8 -*-
"""
Modulo compatibilità Qt5 / Qt6 basato sul layer nativo QGIS (qgis.PyQt).
Evita import diretti di PyQt5 / PyQt6 per piena conformità ai check ufficiali Qt6 di QGIS.
"""
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtCore import Qt, QDate, QVariant
from qgis.PyQt.QtGui import QIcon, QPixmap, QImage, QColor
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox,
    QAbstractItemView, QSpinBox, QGroupBox, QFileDialog,
    QProgressBar, QDialog, QTextEdit, QTabWidget, QRadioButton,
    QButtonGroup, QFormLayout
)
