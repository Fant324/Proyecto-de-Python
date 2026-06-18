"""Módulo de diálogo base sin decoración nativa del sistema"""

import logging
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)

logger = logging.getLogger(__name__)


class BaseDialog(QDialog):
    """Diálogo base sin barra de título del sistema, con encabezado personalizado y botón de cerrar"""
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setModal(True)
        self.drag_position = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("titleBar")
        header.setAutoFillBackground(True)
        palette = header.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0d3b4f"))
        header.setPalette(palette)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 4, 6, 4)
        header_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #cde5f5; font-weight: bold; font-size: 14px;"
        )
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(38, 28)
        close_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: transparent;"
            "  color: #ffffff;"
            "  border: none;"
            "  font-size: 18px;"
            "  font-weight: bold;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #c0392b;"
            "}"
        )
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        self.main_layout.addWidget(header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 16, 20, 16)
        self.content_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_layout)

        self.setLayout(self.main_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
