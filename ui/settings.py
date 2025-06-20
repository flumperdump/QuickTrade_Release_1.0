from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy, QFrame
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

class CollapsibleBox(QGroupBox):
    def __init__(self, title):
        super().__init__()
        self.setTitle("")
        self.toggle_button = QToolButton(text=title, checkable=True, checked=True)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_button.clicked.connect(self.toggle_content)

        self.content = QWidget()
        self.content.setLayout(QVBoxLayout())

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def toggle_content(self):
        visible = not self.content.isVisible()
        self.content.setVisible(visible)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow)

    def add_widget(self, widget):
        self.content.layout().addWidget(widget)

class SettingsTab(QWidget):
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        self.user_prefs = self.load_config()
        self.api_data = self.load_api_keys()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])

        choose_btn = QPushButton("Choose Exchanges")
        choose_btn.clicked.connect(self.choose_exchanges)
        self.container.layout().addWidget(choose_btn)

        self.api_box = QGroupBox("Manage API Keys")
        self.api_layout = QVBoxLayout()

        self.api_box.setLayout(self.api_layout)
        self.container.layout().addWidget(self.api_box)

        scroll.setWidget(self.container)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.render_exchange_sections()

    def render_exchange_sections(self):
        for i in reversed(range(self.api_layout.count())):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for ex in self.selected_exchanges:
            exchange_box = CollapsibleBox(ex)

            subaccounts = self.api_data.get(ex, {})
            for subaccount, creds in subaccounts.items():
                self.create_subaccount_widget(exchange_box, ex, subaccount, creds, editable=False)

            add_sub_btn = QPushButton(f"Add Subaccount to {ex}")
            add_sub_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            exchange_box.add_widget(add_sub_btn)
            self.api_layout.addWidget(exchange_box)

    def create_subaccount_widget(self, exchange_box, ex, subaccount, creds, editable):
        sub_box = QGroupBox()
        sub_box.setLayout(QFormLayout())

        sub_name_input = QLineEdit(subaccount)
        sub_name_input.setDisabled(not editable)

        api_key_input = QLineEdit(creds.get("api_key", ""))
        api_key_input.setDisabled(not editable)
        api_secret_input = QLineEdit(creds.get("api_secret", ""))
        api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_secret_input.setDisabled(not editable)

        save_btn = QPushButton("Save")
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        def save():
            new_name = sub_name_input.text().strip()
            key = api_key_input.text().strip()
            secret = api_secret_input.text().strip()
            if not new_name or not key or not secret:
                QMessageBox.warning(self, "Missing Info", "All fields must be filled.")
                return
            if new_name != subaccount:
                self.api_data[ex].pop(subaccount, None)
                subaccount_key = new_name
            else:
                subaccount_key = subaccount
            self.api_data[ex][subaccount_key] = {"api_key": key, "api_secret": secret}
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(self.api_data, f, indent=2)
            sub_name_input.setDisabled(True)
            api_key_input.setDisabled(True)
            api_secret_input.setDisabled(True)
            save_btn.setDisabled(True)
            edit_btn.setDisabled(False)
            QMessageBox.information(self, "Saved", f"Keys for {ex} → {subaccount_key} saved.")

        def edit():
            sub_name_input.setDisabled(False)
            api_key_input.setDisabled(False)
            api_secret_input.setDisabled(False)
            save_btn.setDisabled(False)
            edit_btn.setDisabled(True)

        def delete():
            self.api_data[ex].pop(subaccount, None)
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(self.api_data, f, indent=2)
            self.render_exchange_sections()

        save_btn.clicked.connect(save)
        edit_btn.clicked.connect(edit)
        delete_btn.clicked.connect(delete)

        h = QHBoxLayout()
        h.addWidget(save_btn)
        if not editable:
            h.addWidget(edit_btn)
        h.addWidget(delete_btn)

        sub_box.layout().addRow("Subaccount Name:", sub_name_input)
        sub_box.layout().addRow("API Key:", api_key_input)
        sub_box.layout().addRow("API Secret:", api_secret_input)
        sub_box.layout().addRow(h)

        exchange_box.add_widget(sub_box)

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            selected = dialog.get_selected()
            self.selected_exchanges = selected
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({"enabled_exchanges": selected}, f, indent=2)
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

    def add_subaccount(self, exchange):
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        subaccount = f"Sub{len(self.api_data[exchange]) + 1}"
        self.api_data[exchange][subaccount] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        self.render_exchange_sections()
        # Set the new subaccount editable by default
        # Re-render will catch it and allow edit mode immediately

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
