from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox,
    QGroupBox, QGridLayout, QLineEdit, QMessageBox, QScrollArea, QHBoxLayout,
    QFormLayout, QDialog, QListWidget, QListWidgetItem
)
import json
import os

CONFIG_PATH = "config/user_prefs.json"
API_KEYS_PATH = "config/api_keys.json"

SUPPORTED_EXCHANGES = [
    "Bybit", "Kraken", "Binance", "KuCoin", "Coinbase", "MEXC",
    "Bitget", "Crypto.com", "Hyperliquid"
]

class ExchangeSelectorDialog(QDialog):
    def __init__(self, parent, selected_exchanges):
        super().__init__(parent)
        self.setWindowTitle("Choose Exchanges")
        self.setLayout(QVBoxLayout())
        self.selected_exchanges = selected_exchanges.copy()

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for ex in SUPPORTED_EXCHANGES:
            item = QListWidgetItem(ex)
            item.setSelected(ex in selected_exchanges)
            self.list_widget.addItem(item)
        self.layout().addWidget(self.list_widget)

        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("Confirm?"))
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        confirm_layout.addWidget(yes_btn)
        confirm_layout.addWidget(no_btn)
        self.layout().addLayout(confirm_layout)

        yes_btn.clicked.connect(self.accept)
        no_btn.clicked.connect(self.reject)

    def get_selected(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if self.list_widget.item(i).isSelected()]

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setLayout(QVBoxLayout())

        choose_btn = QPushButton("Choose Exchanges")
        choose_btn.clicked.connect(self.choose_exchanges)
        container.layout().addWidget(choose_btn)

        self.exchanges_box = QGroupBox("Enabled Exchanges")
        self.ex_layout = QVBoxLayout()
        self.checkboxes = {}

        for ex in SUPPORTED_EXCHANGES:
            cb = QCheckBox(ex)
            self.ex_layout.addWidget(cb)
            self.checkboxes[ex] = cb
        self.exchanges_box.setLayout(self.ex_layout)

        self.save_ex_btn = QPushButton("Save Exchange Selection")
        self.save_ex_btn.clicked.connect(self.save_exchanges)

        container.layout().addWidget(self.exchanges_box)
        container.layout().addWidget(self.save_ex_btn)

        self.api_box = QGroupBox("Manage API Keys")
        self.api_layout = QVBoxLayout()
        self.api_forms = {}
        self.api_data = self.load_api_keys()

        for ex in SUPPORTED_EXCHANGES:
            if ex in self.api_data:
                exchange_box = QGroupBox(ex)
                exchange_box.setCheckable(True)
                exchange_box.setChecked(True)
                exchange_layout = QVBoxLayout()

                for subaccount, creds in self.api_data[ex].items():
                    sub_box = QGroupBox(subaccount)
                    sub_box.setCheckable(True)
                    sub_box.setChecked(True)
                    sub_layout = QFormLayout()

                    api_key_input = QLineEdit(creds.get("api_key", ""))
                    api_secret_input = QLineEdit(creds.get("api_secret", ""))
                    api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)

                    save_btn = QPushButton("Save")
                    save_btn.clicked.connect(lambda _, e=ex, s=subaccount, k=api_key_input, sec=api_secret_input: self.save_api(e, s, k, sec))

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

        self.api_box.setLayout(self.api_layout)
        container.layout().addWidget(self.api_box)

        scroll.setWidget(container)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.load_config()

    def choose_exchanges(self):
        current = [ex for ex, cb in self.checkboxes.items() if cb.isChecked()]
        dialog = ExchangeSelectorDialog(self, current)
        if dialog.exec():
            selected = dialog.get_selected()
            for ex, cb in self.checkboxes.items():
                cb.setChecked(ex in selected)
            self.save_exchanges()

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

        QMessageBox.information(self, "Saved", f"API keys for {exchange} → {subaccount} saved.")

    def add_subaccount(self, exchange):
        subaccount = f"Sub{len(self.api_data.get(exchange, {})) + 1}"
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        self.api_data[exchange][subaccount] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        QMessageBox.information(self, "Added", f"Subaccount {subaccount} added to {exchange}. Please refresh Settings tab to see changes.")

    def save_exchanges(self):
        selected = [ex for ex, cb in self.checkboxes.items() if cb.isChecked()]
        os.makedirs("config", exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"enabled_exchanges": selected}, f, indent=2)
        QMessageBox.information(self, "Saved", "Exchange selection saved.")

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                for ex in data.get("enabled_exchanges", []):
                    if ex in self.checkboxes:
                        self.checkboxes[ex].setChecked(True)

    def load_api_keys(self):
        if os.path.exists(API_KEYS_PATH):
            with open(API_KEYS_PATH, 'r') as f:
                return json.load(f)
        return {}
