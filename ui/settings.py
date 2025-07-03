import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QLineEdit,
    QHBoxLayout, QGroupBox, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

CONFIG_PATH = "config/user_prefs.json"
API_KEYS_PATH = "config/api_keys.json"

class SettingsTab(QWidget):
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated

        self.api_data = self.load_api_keys()
        self.user_prefs = self.load_config()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])
        self.available_exchanges = ["Binance", "Kraken", "KuCoin", "Bybit", "MEXC", "Coinbase", "Bitget", "Crypto.com", "Hyperliquid"]
        self.exchange_checkboxes = {}
        self.active_subaccount_row = None

        layout = QVBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)

        layout.addWidget(QLabel("Select Exchanges to Enable:"))

        for ex in self.available_exchanges:
            cb = QCheckBox(ex)
            cb.setChecked(ex in self.selected_exchanges)
            self.exchange_checkboxes[ex] = cb
            layout.addWidget(cb)

        confirm_btn = QPushButton("Confirm Exchanges")
        confirm_btn.clicked.connect(self.confirm_exchanges)
        layout.addWidget(confirm_btn)

        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self.render_exchange_sections()

    def load_api_keys(self):
        if os.path.exists(API_KEYS_PATH):
            with open(API_KEYS_PATH, 'r') as f:
                return json.load(f)
        return {}

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def confirm_exchanges(self):
        self.selected_exchanges = [ex for ex, cb in self.exchange_checkboxes.items() if cb.isChecked()]
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
            group = QGroupBox(exchange)
            group_layout = QVBoxLayout()

            add_btn = QPushButton("Add Subaccount")
            add_btn.clicked.connect(lambda _, ex=exchange: self.add_subaccount_blank(ex))
            group_layout.addWidget(add_btn)

            if exchange in self.api_data:
                for sub, creds in self.api_data[exchange].items():
                    group_layout.addLayout(self.build_subaccount_row(exchange, sub, creds))

            group.setLayout(group_layout)
            self.scroll_layout.addWidget(group)

        self.scroll_layout.addStretch()

    def build_subaccount_row(self, exchange, subaccount, creds):
        row = QHBoxLayout()
        name_edit = QLineEdit(subaccount)
        key_edit = QLineEdit(creds.get("api_key", ""))
        secret_edit = QLineEdit(creds.get("api_secret", ""))
        key_edit.setPlaceholderText("API Key")
        secret_edit.setPlaceholderText("API Secret")

        save_btn = QPushButton("Save")
        delete_btn = QPushButton("Delete")

        def save():
            new_sub = name_edit.text().strip()
            key = key_edit.text().strip()
            secret = secret_edit.text().strip()
            if not new_sub or not key or not secret:
                QMessageBox.warning(self, "Missing Fields", "Please fill all fields to save.")
                return

            if exchange not in self.api_data:
                self.api_data[exchange] = {}
            if new_sub != subaccount:
                self.api_data[exchange].pop(subaccount, None)
            self.api_data[exchange][new_sub] = {"api_key": key, "api_secret": secret}
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(self.api_data, f, indent=2)

            self.active_subaccount_row = None
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

        def delete():
            if exchange in self.api_data:
                self.api_data[exchange].pop(subaccount, None)
                if not self.api_data[exchange]:
                    del self.api_data[exchange]
                with open(API_KEYS_PATH, 'w') as f:
                    json.dump(self.api_data, f, indent=2)
                self.render_exchange_sections()
                if self.on_exchanges_updated:
                    self.on_exchanges_updated()

        save_btn.clicked.connect(save)
        delete_btn.clicked.connect(delete)

        row.addWidget(QLabel("Subaccount:"))
        row.addWidget(name_edit)
        row.addWidget(key_edit)
        row.addWidget(secret_edit)
        row.addWidget(save_btn)
        row.addWidget(delete_btn)

        return row

    def add_subaccount_blank(self, exchange):
        if self.active_subaccount_row:
            QMessageBox.warning(self, "Complete Current Edit", "Please save or delete the current subaccount being edited before adding a new one.")
            return

        if exchange not in self.api_data:
            self.api_data[exchange] = {}

        new_name = f"Sub{len(self.api_data[exchange]) + 1}"
        self.api_data[exchange][new_name] = {"api_key": "", "api_secret": ""}
        self.active_subaccount_row = new_name
        self.render_exchange_sections()
