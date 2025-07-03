from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QDialog, QDialogButtonBox,
    QGroupBox, QToolButton, QSizePolicy, QCheckBox
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
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
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

class SettingsTab(QWidget):
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated
        self.active_edit = None
        self.user_prefs = self.load_config()
        self.api_data = self.load_api_keys()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])

        layout = QVBoxLayout()

        self.choose_btn = QPushButton("Choose Exchanges")
        self.choose_btn.clicked.connect(self.choose_exchanges)
        layout.addWidget(self.choose_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_container.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_container)
        layout.addWidget(self.scroll)

        self.setLayout(layout)
        self.render_exchange_sections()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def load_api_keys(self):
        if os.path.exists(API_KEYS_PATH):
            with open(API_KEYS_PATH, 'r') as f:
                return json.load(f)
        return {}

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            self.selected_exchanges = dialog.get_selected()
            self.user_prefs["enabled_exchanges"] = self.selected_exchanges
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.user_prefs, f, indent=2)
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

    def render_exchange_sections(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for exchange in self.selected_exchanges:
            box = CollapsibleBox(exchange)
            subaccounts = self.api_data.get(exchange, {})
            for name, creds in subaccounts.items():
                self.add_subaccount_row(box, exchange, name, creds)
            add_btn = QPushButton(f"Add Subaccount to {exchange}")
            add_btn.clicked.connect(lambda _, ex=exchange: self.add_subaccount_blank(ex))
            box.add_widget(add_btn)
            self.scroll_layout.addWidget(box)

    def add_subaccount_row(self, container, exchange, name, creds):
        row = QWidget()
        layout = QFormLayout()
        row.setLayout(layout)

        name_input = QLineEdit(name)
        key_input = QLineEdit(creds.get("api_key", ""))
        secret_input = QLineEdit(creds.get("api_secret", ""))
        secret_input.setEchoMode(QLineEdit.EchoMode.Password)

        save_btn = QPushButton("Save")
        delete_btn = QPushButton("Delete")

        def save():
            new_name = name_input.text().strip()
            key = key_input.text().strip()
            secret = secret_input.text().strip()
            if not new_name or not key or not secret:
                QMessageBox.warning(self, "Missing Info", "All fields are required.")
                return
            if exchange not in self.api_data:
                self.api_data[exchange] = {}
            if new_name != name:
                self.api_data[exchange].pop(name, None)
            self.api_data[exchange][new_name] = {"api_key": key, "api_secret": secret}
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(self.api_data, f, indent=2)
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

        def delete():
            if exchange in self.api_data and name in self.api_data[exchange]:
                del self.api_data[exchange][name]
                with open(API_KEYS_PATH, 'w') as f:
                    json.dump(self.api_data, f, indent=2)
                self.render_exchange_sections()
                if self.on_exchanges_updated:
                    self.on_exchanges_updated()

        save_btn.clicked.connect(save)
        delete_btn.clicked.connect(delete)

        row_layout = QHBoxLayout()
        row_layout.addWidget(save_btn)
        row_layout.addWidget(delete_btn)

        layout.addRow("Subaccount Name", name_input)
        layout.addRow("API Key", key_input)
        layout.addRow("API Secret", secret_input)
        layout.addRow(row_layout)

        container.add_widget(row)

    def add_subaccount_blank(self, exchange):
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        new_name = f"Sub{len(self.api_data[exchange]) + 1}"
        self.api_data[exchange][new_name] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        self.render_exchange_sections()
