from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox,
    QGroupBox, QGridLayout, QLineEdit, QMessageBox, QScrollArea, QHBoxLayout,
    QFormLayout, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
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
    def __init__(self):
        super().__init__()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
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

        self.api_box.setLayout(self.api_layout)
        self.container.layout().addWidget(self.api_box)

        self.scroll.setWidget(self.container)
        layout = QVBoxLayout()
        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self.render_exchange_sections()

    def render_exchange_sections(self):
        # Clear old widgets
        while self.api_layout.count():
            child = self.api_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for ex in self.selected_exchanges:
            exchange_box = QGroupBox(ex)
            exchange_box.setCheckable(False)
            exchange_layout = QVBoxLayout()

            subaccounts = self.api_data.get(ex, {})
            for subaccount, creds in subaccounts.items():
                sub_box = QGroupBox(subaccount)
                sub_box.setCheckable(False)
                sub_layout = QFormLayout()

                name_input = QLineEdit(subaccount)
                name_input.setPlaceholderText("Subaccount Name")
                name_input.textChanged.connect(lambda new_name, e=ex, old=subaccount: self.rename_subaccount(e, old, new_name))

                api_key_input = QLineEdit(creds.get("api_key", ""))
                api_secret_input = QLineEdit(creds.get("api_secret", ""))
                api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)

                save_btn = QPushButton("Save")
                save_btn.clicked.connect(lambda _, e=ex, s=subaccount, k=api_key_input, sec=api_secret_input: self.save_api(e, s, k, sec))

                sub_layout.addRow("Subaccount:", name_input)
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

        self.api_box.update()
        self.container.update()
        self.scroll.update()
        self.update()

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            selected = dialog.get_selected()
            self.selected_exchanges = selected
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({"enabled_exchanges": selected}, f, indent=2)
            self.render_exchange_sections()

    def save_api(self, exchange, subaccount, key_input, secret_input):
        key = key_input.text().strip()
        secret = secret_input.text().strip()

        if not key or not secret:
            QMessageBox.warning(self, "Missing Info", "API key and secret cannot be empty.")
            return

        os.makedirs("config", exist_ok=True)
        if exchange not in self.api_data:
            self.api_data[exchange] = {}

        self.api_data[exchange][subaccount] = {"api_key": key, "api_secret": secret}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)

    def add_subaccount(self, exchange):
        subaccounts = self.api_data.get(exchange, {})
        i = 1
        new_label = f"Sub{i}"
        while new_label in subaccounts:
            i += 1
            new_label = f"Sub{i}"

        self.api_data.setdefault(exchange, {})[new_label] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        self.render_exchange_sections()

    def rename_subaccount(self, exchange, old_name, new_name):
        if old_name != new_name and new_name:
            exchange_data = self.api_data.get(exchange, {})
            if old_name in exchange_data:
                exchange_data[new_name] = exchange_data.pop(old_name)
                with open(API_KEYS_PATH, 'w') as f:
                    json.dump(self.api_data, f, indent=2)

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
