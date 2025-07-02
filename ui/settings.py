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
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        self.choose_btn = QPushButton("Choose Exchanges")
        self.choose_btn.clicked.connect(self.choose_exchanges)
        self.container.layout().addWidget(self.choose_btn)

        self.api_box = QGroupBox("Manage API Keys")
        self.api_layout = QVBoxLayout()
        self.api_box.setLayout(self.api_layout)
        self.container.layout().addWidget(self.api_box)

        scroll.setWidget(self.container)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.user_prefs = self.load_config()
        self.api_data = self.load_api_keys()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])

        self.render_exchange_sections()

    def choose_exchanges(self):
        dialog = ExchangeSelectorDialog(self, self.selected_exchanges)
        if dialog.exec():
            self.selected_exchanges = dialog.get_selected()
            self.save_config()
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

    def render_exchange_sections(self):
        for i in reversed(range(self.api_layout.count())):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for ex in self.selected_exchanges:
            ex_group = QGroupBox(ex)
            ex_layout = QVBoxLayout()
            subaccounts = self.api_data.get(ex, {})
            for subaccount, creds in subaccounts.items():
                ex_layout.addLayout(self.create_subaccount_form(ex, subaccount, creds))

            add_btn = QPushButton(f"Add Subaccount to {ex}")
            add_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            ex_layout.addWidget(add_btn)

            ex_group.setLayout(ex_layout)
            self.api_layout.addWidget(ex_group)

    def create_subaccount_form(self, exchange, subaccount, creds):
        layout = QFormLayout()
        api_key = QLineEdit(creds.get("api_key", ""))
        api_secret = QLineEdit(creds.get("api_secret", ""))
        api_secret.setEchoMode(QLineEdit.EchoMode.Password)

        save_btn = QPushButton("Save")
        save_btn.setEnabled(False)
        save_btn.setStyleSheet("background-color: lightgrey;")

        def enable_save():
            if api_key.text().strip():
                save_btn.setEnabled(True)
                save_btn.setStyleSheet("")
            else:
                save_btn.setEnabled(False)
                save_btn.setStyleSheet("background-color: lightgrey;")

        api_key.textChanged.connect(enable_save)
        api_secret.textChanged.connect(enable_save)

        def save():
            key = api_key.text().strip()
            secret = api_secret.text().strip()
            if not key:
                QMessageBox.warning(self, "Missing Info", "API key cannot be empty.")
                return

            self.api_data.setdefault(exchange, {})[subaccount] = {"api_key": key, "api_secret": secret}
            self.save_api_keys()
            QMessageBox.information(self, "Saved", f"Saved credentials for {subaccount} on {exchange}.")

            if self.on_exchanges_updated:
                self.on_exchanges_updated()

        save_btn.clicked.connect(save)

        row = QHBoxLayout()
        row.addWidget(save_btn)
        delete_btn = QPushButton("Delete")

        def delete():
            confirm = QMessageBox.question(self, "Confirm", f"Delete subaccount '{subaccount}'?")
            if confirm == QMessageBox.StandardButton.Yes:
                del self.api_data[exchange][subaccount]
                self.save_api_keys()
                self.render_exchange_sections()
                if self.on_exchanges_updated:
                    self.on_exchanges_updated()

        delete_btn.clicked.connect(delete)
        row.addWidget(delete_btn)

        layout.addRow("Subaccount:", QLabel(subaccount))
        layout.addRow("API Key:", api_key)
        layout.addRow("API Secret:", api_secret)
        layout.addRow(row)
        return layout

    def add_subaccount(self, exchange):
        count = len(self.api_data.get(exchange, {})) + 1
        name = f"Sub{count}"
        self.api_data.setdefault(exchange, {})[name] = {"api_key": "", "api_secret": ""}
        self.save_api_keys()
        self.render_exchange_sections()

    def save_api_keys(self):
        os.makedirs("config", exist_ok=True)
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)

    def save_config(self):
        os.makedirs("config", exist_ok=True)
        self.user_prefs["enabled_exchanges"] = self.selected_exchanges
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.user_prefs, f, indent=2)

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
