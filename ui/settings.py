from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy, QFrame, QSpacerItem
)
from PyQt6.QtCore import Qt, QPropertyAnimation
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
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold;")
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.clicked.connect(self.toggle)

        self.content_area = QFrame()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setMaximumHeight(0)

        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)

        self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(150)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        layout.setContentsMargins(0, 0, 0, 0)

        self.expanded_height = 0
        self.is_expanded = False

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
        self.expanded_height += widget.sizeHint().height() + 10
        if self.toggle_button.isChecked():
            self.content_area.setMaximumHeight(self.expanded_height)

    def toggle(self):
        self.is_expanded = not self.is_expanded
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if self.is_expanded else Qt.ArrowType.RightArrow)
        new_height = self.expanded_height if self.is_expanded else 0
        self.toggle_animation.stop()
        self.toggle_animation.setEndValue(new_height)
        self.toggle_animation.start()

class SettingsTab(QWidget):
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated
        self.active_add = False

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        self.user_prefs = self.load_config()
        self.api_data = self.load_api_keys()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])

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

        self.render_exchange_sections()

    def set_controls_enabled(self, enabled):
        self.choose_btn.setEnabled(enabled)
        for i in range(self.api_layout.count()):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.setEnabled(enabled)

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

                save_btn.setMinimumWidth(60)
                edit_btn.setMinimumWidth(60)
                delete_btn.setMinimumWidth(60)

                def make_save_func(ex=ex, old_sub=subaccount, name_input=sub_name_input, k=api_key_input, s=api_secret_input):
                    def save():
                        new_sub = name_input.text().strip()
                        key = k.text().strip()
                        secret = s.text().strip()
                        if not new_sub or not key or not secret:
                            return
                        if new_sub != old_sub:
                            self.api_data[ex].pop(old_sub, None)
                        self.api_data[ex][new_sub] = {"api_key": key, "api_secret": secret}
                        with open(API_KEYS_PATH, 'w') as f:
                            json.dump(self.api_data, f, indent=2)

                        name_input.setDisabled(True)
                        k.setDisabled(True)
                        s.setDisabled(True)
                        save_btn.setDisabled(True)
                        edit_btn.setVisible(True)

                        self.active_add = False
                        self.set_controls_enabled(True)
                        self.render_exchange_sections()
                    return save

                def make_edit_func():
                    def edit():
                        sub_name_input.setDisabled(False)
                        api_key_input.setDisabled(False)
                        api_secret_input.setDisabled(False)
                        save_btn.setDisabled(False)
                        edit_btn.setVisible(False)
                    return edit

                def make_delete_func(ex=ex, sub=subaccount):
                    def delete():
                        confirm = QMessageBox.question(
                            self, "Delete Subaccount?",
                            f"Are you sure you want to delete {sub}?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if confirm == QMessageBox.StandardButton.Yes:
                            if ex in self.api_data and sub in self.api_data[ex]:
                                del self.api_data[ex][sub]
                                with open(API_KEYS_PATH, 'w') as f:
                                    json.dump(self.api_data, f, indent=2)
                                self.active_add = False
                                self.set_controls_enabled(True)
                                self.render_exchange_sections()
                    return delete

                is_new = creds["api_key"] == "" and creds["api_secret"] == ""
                if is_new:
                    edit_btn.setVisible(False)
                    self.active_add = True
                    self.set_controls_enabled(False)
                else:
                    sub_name_input.setDisabled(True)
                    api_key_input.setDisabled(True)
                    api_secret_input.setDisabled(True)
                    save_btn.setDisabled(True)
                    edit_btn.clicked.connect(make_edit_func())

                save_btn.clicked.connect(make_save_func())
                delete_btn.clicked.connect(make_delete_func())

                row = QHBoxLayout()
                row.addWidget(save_btn)
                row.addWidget(edit_btn)
                row.addWidget(delete_btn)
                row.addStretch()

                sub_box.layout().addRow("Subaccount Name:", sub_name_input)
                sub_box.layout().addRow("API Key:", api_key_input)
                sub_box.layout().addRow("API Secret:", api_secret_input)
                sub_box.layout().addRow(row)

                exchange_box.add_widget(sub_box)

            add_sub_btn = QPushButton(f"Add Subaccount to {ex}")
            add_sub_btn.setMinimumHeight(28)
            add_sub_btn.setMinimumWidth(180)
            add_sub_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            add_sub_btn.setEnabled(not self.active_add)
            exchange_box.add_widget(add_sub_btn)

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
        if self.active_add:
            return
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
