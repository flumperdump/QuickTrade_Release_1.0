from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox,
    QGroupBox, QGridLayout, QLineEdit, QMessageBox, QScrollArea, QHBoxLayout,
    QFormLayout, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QToolButton
)
from PyQt6.QtCore import Qt
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
        self.exchange_list = QListWidget()
        self.exchange_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        for ex in SUPPORTED_EXCHANGES:
            item = QListWidgetItem(ex)
            item.setSelected(ex in selected_exchanges)
            self.exchange_list.addItem(item)

        layout.addWidget(QLabel("Select exchanges to enable:"))
        layout.addWidget(self.exchange_list)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Confirm?"))
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected(self):
        return [self.exchange_list.item(i).text() for i in range(self.exchange_list.count()) if self.exchange_list.item(i).isSelected()]

class SettingsTab(QWidget):
    def __init__(self, refresh_ui_callback=None):
        super().__init__()
        self.refresh_ui_callback = refresh_ui_callback

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        self.user_prefs = self.load_config()
        self.api_data = self.load_api_keys()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", SUPPORTED_EXCHANGES)

        choose_btn = QPushButton("Choose Exchanges")
        choose_btn.clicked.connect(self.choose_exchanges)
        self.container.layout().addWidget(choose_btn)

        self.api_box = QGroupBox("Manage API Keys")
        self.api_layout = QVBoxLayout()
        self.api_forms = {}

        self.render_exchange_sections()

        self.api_box.setLayout(self.api_layout)
        self.container.layout().addWidget(self.api_box)

        scroll.setWidget(self.container)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

    def render_exchange_sections(self):
        for ex in self.selected_exchanges:
            exchange_box = QGroupBox(ex)
            exchange_layout = QVBoxLayout()

            subaccounts = self.api_data.get(ex, {})
            for subaccount, creds in subaccounts.items():
                sub_box = QGroupBox(subaccount)
                sub_layout = QFormLayout()

                rename_input = QLineEdit(subaccount)
                rename_input.setPlaceholderText("Rename Subaccount")

                api_key_input = QLineEdit(creds.get("api_key", ""))
                api_secret_input = QLineEdit(creds.get("api_secret", ""))
                api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)

                save_btn = QPushButton("Save")
                save_btn.clicked.connect(lambda _, e=ex, r=rename_input, k=api_key_input, s=api_secret_input, old=subaccount: self.save_api(e, r, k, s, old))

                sub_layout.addRow("Rename:", rename_input)
                sub_layout.addRow("API Key:", api_key_input)
                sub_layout.addRow("API Secret:", api_secret_input)
                sub_layout.addRow(save_btn)
                sub_box.setLayout(sub_layout)
                exchange_layout.addWidget(sub_box)

            add_sub_btn = QPushButton(f"Add Subaccount to {ex}")
            add_sub_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            exchange_layout.addWidget(add_sub_btn)

            exchange_box.setLayout(exchange_layout)
            self.api_layout.addWidget(exchange_box)

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            selected = dialog.get_selected()
            self.selected_exchanges = selected
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({"enabled_exchanges": selected}, f, indent=2)
            QMessageBox.information(self, "Saved", "Exchange selection saved. UI will refresh.")
            if self.refresh_ui_callback:
                self.refresh_ui_callback()

    def save_api(self, exchange, rename_input, key_input, secret_input, old_name):
        new_name = rename_input.text().strip()
        key = key_input.text().strip()
        secret = secret_input.text().strip()

        if not key or not secret or not new_name:
            QMessageBox.warning(self, "Missing Info", "API key, secret, and subaccount name cannot be empty.")
            return

        os.makedirs("config", exist_ok=True)
        if exchange not in self.api_data:
            self.api_data[exchange] = {}

        # Handle renaming
        if old_name != new_name:
            self.api_data[exchange].pop(old_name, None)
        self.api_data[exchange][new_name] = {"api_key": key, "api_secret": secret}

        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)

        QMessageBox.information(self, "Saved", f"API keys for {exchange} → {new_name} saved.")

    def add_subaccount(self, exchange):
        subaccount = f"Sub{len(self.api_data.get(exchange, {})) + 1}"
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        self.api_data[exchange][subaccount] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        QMessageBox.information(self, "Added", f"Subaccount {subaccount} added to {exchange}. Please re-open Settings tab to see changes.")

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
