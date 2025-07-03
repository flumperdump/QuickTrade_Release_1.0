import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel, QComboBox, QLineEdit,
    QHBoxLayout, QMessageBox, QGroupBox, QSizePolicy, QSpacerItem, QCheckBox, QFormLayout, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

CONFIG_PATH = "config/user_prefs.json"
API_KEYS_PATH = "config/api_keys.json"

class CollapsibleBox(QGroupBox):
    def __init__(self, title=""):
        super().__init__()
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        self.setLayout(layout)

        self.toggle_animation_running = False

    def on_toggle(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
        self.content_area.setVisible(checked)
        self.content_area.setMaximumHeight(16777215 if checked else 0)

    def setContentLayout(self, layout):
        self.content_area.setLayout(layout)

class SettingsTab(QWidget):
    def __init__(self, on_exchanges_updated=None):
        super().__init__()
        self.on_exchanges_updated = on_exchanges_updated

        self.setLayout(QVBoxLayout())
        self.api_data = self.load_api_keys()
        self.user_prefs = self.load_config()
        self.selected_exchanges = self.user_prefs.get("enabled_exchanges", [])
        self.active_edit = None

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        self.form_layout = QVBoxLayout()
        container.setLayout(self.form_layout)
        scroll_area.setWidget(container)
        self.layout().addWidget(scroll_area)

        # Save button
        self.save_button = QPushButton("Save All Settings")
        self.save_button.clicked.connect(self.save_all)
        self.layout().addWidget(self.save_button)

        # Render
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

    def save_all(self):
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.user_prefs, f, indent=2)
        QMessageBox.information(self, "Settings Saved", "All settings have been saved successfully.")
        self.active_edit = None
        if self.on_exchanges_updated:
            self.on_exchanges_updated()

    def render_exchange_sections(self):
        # Clear layout
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for ex in self.selected_exchanges:
            box = CollapsibleBox(ex)
            inner_layout = QVBoxLayout()

            subaccounts = self.api_data.get(ex, {})
            if not subaccounts:
                self.api_data.setdefault(ex, {})

            for sub in subaccounts:
                creds = self.api_data[ex].get(sub, {"api_key": "", "api_secret": ""})
                self.build_subaccount_ui(inner_layout, ex, sub, creds)

            add_btn = QPushButton(f"Add Subaccount to {ex}")
            add_btn.clicked.connect(lambda _, ex=ex: self.add_subaccount_blank(ex))
            inner_layout.addWidget(add_btn)

            box.setContentLayout(inner_layout)
            self.form_layout.addWidget(box)

        self.form_layout.addStretch()

    def build_subaccount_ui(self, parent_layout, exchange, subaccount, creds):
        box = QGroupBox(f"{subaccount}:")
        layout = QFormLayout()

        sub_name_input = QLineEdit(subaccount)
        api_key_input = QLineEdit(creds.get("api_key", ""))
        api_secret_input = QLineEdit(creds.get("api_secret", ""))

        layout.addRow("Subaccount Name", sub_name_input)
        layout.addRow("API Key", api_key_input)
        layout.addRow("API Secret", api_secret_input)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        delete_btn = QPushButton("Delete")

        def save():
            new_sub = sub_name_input.text().strip()
            key = api_key_input.text().strip()
            secret = api_secret_input.text().strip()
            if not new_sub or not key or not secret:
                QMessageBox.warning(self, "Missing Fields", "Please fill all fields to save.")
                return

            if exchange not in self.api_data:
                self.api_data[exchange] = {}
            if new_sub != subaccount:
                self.api_data[exchange].pop(subaccount, None)
            self.api_data[exchange][new_sub] = {"api_key": key, "api_secret": secret}

            # Save to config
            self.user_prefs.setdefault("subaccount_settings", {}).setdefault(exchange, {})[new_sub] = {
                "last_pair": "BTC/USDT"
            }

            self.save_all()

        def delete():
            confirm = QMessageBox.question(self, "Delete Subaccount", f"Are you sure you want to delete {subaccount}?")
            if confirm == QMessageBox.StandardButton.Yes:
                self.api_data[exchange].pop(subaccount, None)
                self.user_prefs.get("subaccount_settings", {}).get(exchange, {}).pop(subaccount, None)
                self.save_all()

        save_btn.clicked.connect(save)
        delete_btn.clicked.connect(delete)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(delete_btn)

        layout.addRow(btn_row)
        box.setLayout(layout)
        parent_layout.addWidget(box)

    def add_subaccount_blank(self, exchange):
        if self.active_edit:
            QMessageBox.warning(self, "Unsaved Subaccount", "Please save the current subaccount before adding a new one.")
            return
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        new_name = f"Sub{len(self.api_data[exchange]) + 1}"
        self.api_data[exchange][new_name] = {"api_key": "", "api_secret": ""}
        self.active_edit = new_name
        self.render_exchange_sections()
