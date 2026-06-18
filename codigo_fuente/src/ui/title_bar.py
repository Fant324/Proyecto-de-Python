"""Módulo de la barra de título personalizada sin bordes del sistema"""

import logging
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
)

logger = logging.getLogger(__name__)


class TitleBar(QWidget):
    """Barra de título personalizada con arrastre y botones de minimizar y cerrar"""
    def __init__(self, parent, title="", close_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.drag_position = None

        self.setObjectName("titleBar")
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0d3b4f"))
        self.setPalette(palette)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 4, 6, 4)
        layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "color: #cde5f5; font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.min_btn = QPushButton("─")
        self.close_btn = QPushButton("✕")

        btn_style = (
            "QPushButton {"
            "  background-color: transparent;"
            "  color: #ffffff;"
            "  border: none;"
            "  font-size: 18px;"
            "  font-weight: bold;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #2a6d8f;"
            "}"
        )
        close_style = (
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

        self.min_btn.setFixedSize(38, 28)
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.parent.showMinimized)

        self.close_btn.setFixedSize(38, 28)
        self.close_btn.setStyleSheet(close_style)
        if close_callback:
            self.close_btn.clicked.connect(close_callback)
        else:
            self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.parent.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.parent.move(
                event.globalPosition().toPoint() - self.drag_position
            )
            event.accept()
