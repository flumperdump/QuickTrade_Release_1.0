# ui/settings.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy
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

class CollapsibleBox(QWidget):
    def __init__(self, title):
        super().__init__()
        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.clicked.connect(self.toggle)

        self.content_area = QWidget()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        layout.setContentsMargins(0, 0, 0, 0)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def toggle(self):
        is_expanded = self.content_area.isVisible()
        self.content_area.setVisible(not is_expanded)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if not is_expanded else Qt.ArrowType.RightArrow)

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
                widget.setParent(None)

        for ex in self.selected_exchanges:
            exchange_box = CollapsibleBox(ex)
            subaccounts = self.api_data.get(ex, {})

            for subaccount, creds in subaccounts.items():
                sub_box = QGroupBox()
                sub_box.setLayout(QFormLayout())

                sub_name_input = QLineEdit(subaccount)
                api_key_input = QLineEdit(creds.get("api_key", ""))
                api_secret_input = QLineEdit(creds.get("api_secret", ""))
                api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)

                save_btn = QPushButton("Save")
                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")

                is_new = creds["api_key"] == "" and creds["api_secret"] == ""

                def save_subaccount():
                    new_name = sub_name_input.text().strip()
                    api_key = api_key_input.text().strip()
                    api_secret = api_secret_input.text().strip()
                    if not new_name or not api_key or not api_secret:
                        return

                    if ex not in self.api_data:
                        self.api_data[ex] = {}
                    if new_name != subaccount:
                        self.api_data[ex].pop(subaccount, None)
                    self.api_data[ex][new_name] = {
                        "api_key": api_key,
                        "api_secret": api_secret
                    }
                    with open(API_KEYS_PATH, 'w') as f:
                        json.dump(self.api_data, f, indent=2)

                    sub_name_input.setDisabled(True)
                    api_key_input.setDisabled(True)
                    api_secret_input.setDisabled(True)
                    save_btn.setDisabled(True)
                    edit_btn.setVisible(True)

                def edit_subaccount():
                    sub_name_input.setDisabled(False)
                    api_key_input.setDisabled(False)
                    api_secret_input.setDisabled(False)
                    save_btn.setDisabled(False)
                    edit_btn.setVisible(False)

                def delete_subaccount():
                    confirm = QMessageBox.question(
                        self, "Delete Subaccount?",
                        f"Are you sure you want to delete {subaccount}?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if confirm == QMessageBox.StandardButton.Yes:
                        if ex in self.api_data and subaccount in self.api_data[ex]:
                            del self.api_data[ex][subaccount]
                            with open(API_KEYS_PATH, 'w') as f:
                                json.dump(self.api_data, f, indent=2)
                        self.render_exchange_sections()

                save_btn.clicked.connect(save_subaccount)
                edit_btn.clicked.connect(edit_subaccount)
                delete_btn.clicked.connect(delete_subaccount)

                if is_new:
                    edit_btn.setVisible(False)
                else:
                    sub_name_input.setDisabled(True)
                    api_key_input.setDisabled(True)
                    api_secret_input.setDisabled(True)
                    save_btn.setDisabled(True)

                row = QHBoxLayout()
                row.addWidget(save_btn)
                row.addWidget(edit_btn)
                row.addWidget(delete_btn)

                sub_box.layout().addRow("Subaccount Name:", sub_name_input)
                sub_box.layout().addRow("API Key:", api_key_input)
                sub_box.layout().addRow("API Secret:", api_secret_input)
                sub_box.layout().addRow(row)

                exchange_box.add_widget(sub_box)

            add_btn = QPushButton(f"Add Subaccount to {ex}")
            add_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            exchange_box.add_widget(add_btn)

            self.api_layout.addWidget(exchange_box)

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
        subaccount = f"Sub{len(self.api_data.get(exchange, {})) + 1}"
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        self.api_data[exchange][subaccount] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
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
