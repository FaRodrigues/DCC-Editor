# -*- coding: utf-8 -*-
# gui/widgets.py

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import Qt

class AutoResizingTextEdit(QTextEdit):
    def __init__(self, text=""):
        super().__init__(text)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.document().documentLayout().documentSizeChanged.connect(self.adjust_height)
        self.adjust_height()

    def adjust_height(self):
        doc_height = self.document().documentLayout().documentSize().height()
        self.setFixedHeight(int(doc_height) + 10)
