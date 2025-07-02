
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import json
import os

CONFIG_PATH = "config/user_prefs.json"
API_KEYS_PATH = "config/api_keys.json"

SUPPORTED_EXCHANGES = [
    "Bybit", "Kraken", "Binance", "KuCoin", "Coinbase", "MEXC",
    "Bitget", "Crypto.com", "Hyperliquid"
]

class ExchangeSelectionDialog(QDialog):
    def __init__(self, selected_exchanges):
        super().__init__()
        self.setWindowTitle("Choose Exchanges")
        self.setMinimumWidth(300)
        self.selected_exchanges = selected_exchanges

        layout = QVBoxLayout()
        self.checkboxes = []

        layout.addWidget(QLabel("Select exchanges to enable:"))
        for ex in SUPPORTED_EXCHANGES:
            checkbox = QCheckBox(ex)
            checkbox.setChecked(ex in selected_exchanges)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Confirm?"))
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

class CollapsibleBox(QWidget):
    def __init__(self, title):
        super().__init__()
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold;")
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_button.setToolButtonStyle(QToolButton.ToolButtonTextBesideIcon)
        self.toggle_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.toggle_button.clicked.connect(self.toggle)

        self.content_area = QWidget()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)

        self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(150)
        self.toggle_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.expanded_height = 0
        self.is_expanded = True
        self.locked = False

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
        self.expanded_height += widget.sizeHint().height() + 10
        if self.is_expanded:
            self.content_area.setMaximumHeight(self.expanded_height)

    def toggle(self):
        if self.locked:
            return
        self.is_expanded = not self.is_expanded
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if self.is_expanded else Qt.ArrowType.RightArrow)
        new_height = self.expanded_height if self.is_expanded else 0
        self.toggle_animation.stop()
        self.toggle_animation.setStartValue(self.content_area.maximumHeight())
        self.toggle_animation.setEndValue(new_height)
        self.toggle_animation.start()

    def lock_toggle(self):
        self.locked = True
        self.toggle_button.setEnabled(False)
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold; color: gray;")

    def unlock_toggle(self):
        self.locked = False
        self.toggle_button.setEnabled(True)
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold;")
