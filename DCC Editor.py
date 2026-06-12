# -*- coding: utf-8 -*-
# DCC Editor & Creator version 6.0 (2026) - Modular Version
# Author: Fernando Rodrigues and Gustavo Chieza

import os
import sys
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import QApplication
from gui.main_window import DCCFormEditor, GLOBAL_STYLESHEET

version = "6.0"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    editor = DCCFormEditor(base_dir, version)
    editor.show()

    app_icon = QtGui.QIcon()
    icon_path = os.path.join(base_dir, "gui", "icons", "inmetro.ico")
    if os.path.exists(icon_path):
        app_icon.addFile(icon_path, QtCore.QSize(256, 256))
        app.setWindowIcon(app_icon)

    styles = QtWidgets.QStyleFactory.keys()
    if styles:
        app.setStyle(QtWidgets.QStyleFactory.create(styles[-1]))

    sys.exit(app.exec())
