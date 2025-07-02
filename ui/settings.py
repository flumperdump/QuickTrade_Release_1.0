from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QDialog, QDialogButtonBox,
    QGroupBox, QToolButton, QSizePolicy, QSpacerItem, QCheckBox
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
        self.active_edit = None  # (exchange, subaccount)
        self.exchange_boxes = {}

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

    def save_api_keys(self):
        os.makedirs("config", exist_ok=True)
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)

    def save_user_prefs(self):
        os.makedirs("config", exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.user_prefs, f, indent=2)

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            selected = dialog.get_selected()
            self.selected_exchanges = selected
            self.user_prefs["enabled_exchanges"] = selected
            self.save_user_prefs()
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

    def render_exchange_sections(self):
        for i in reversed(range(self.api_layout.count())):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.exchange_boxes = {}

        for ex in self.selected_exchanges:
            box = CollapsibleBox(ex)
            self.exchange_boxes[ex] = box
            subaccounts = self.api_data.get(ex, {})

            for sub_name, creds in subaccounts.items():
                if not creds.get("api_key"):
                    continue  # Do not load subaccounts with no API key

                self.add_subaccount_ui(box, ex, sub_name, creds, is_new=False)

            add_btn = QPushButton(f"Add Subaccount to {ex}")
            add_btn.clicked.connect(lambda _, e=ex: self.create_subaccount(e))
            box.add_widget(add_btn)

            self.api_layout.addWidget(box)

    def create_subaccount(self, exchange):
        if self.active_edit:
            return
        name = f"Sub{len(self.api_data.get(exchange, {})) + 1}"
        self.api_data.setdefault(exchange, {})[name] = {"api_key": "", "api_secret": ""}
        self.add_subaccount_ui(self.exchange_boxes[exchange], exchange, name, {"api_key": "", "api_secret": ""}, is_new=True)

    def add_subaccount_ui(self, parent_box, exchange, name, creds, is_new):
        group = QGroupBox()
        layout = QFormLayout(group)

        name_input = QLineEdit(name)
        key_input = QLineEdit(creds.get("api_key", ""))
        secret_input = QLineEdit(creds.get("api_secret", ""))
        secret_input.setEchoMode(QLineEdit.EchoMode.Password)

        save_btn = QPushButton("Save")
        save_btn.setEnabled(False)
        save_btn.setStyleSheet("background-color: lightgrey")
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        def validate_inputs():
            if key_input.text().strip():
                save_btn.setEnabled(True)
                save_btn.setStyleSheet("")
            else:
                save_btn.setEnabled(False)
                save_btn.setStyleSheet("background-color: lightgrey")

        name_input.textChanged.connect(validate_inputs)
        key_input.textChanged.connect(validate_inputs)

        def save():
            nonlocal name
            new_name = name_input.text().strip()
            key = key_input.text().strip()
            secret = secret_input.text().strip()

            if not key:
                return

            if new_name != name:
                del self.api_data[exchange][name]
                name = new_name

            self.api_data[exchange][new_name] = {"api_key": key, "api_secret": secret}
            self.save_api_keys()
            self.active_edit = None
            self.render_exchange_sections()
            if self.on_exchanges_updated:
                self.on_exchanges_updated()

        def edit():
            if self.active_edit:
                return
            self.active_edit = (exchange, name)
            for box in self.exchange_boxes.values():
                box.lock_toggle()
            for i in range(self.api_layout.count()):
                w = self.api_layout.itemAt(i).widget()
                if w != parent_box:
                    w.setDisabled(True)
            name_input.setDisabled(False)
            key_input.setDisabled(False)
            secret_input.setDisabled(False)
            save_btn.setEnabled(bool(key_input.text().strip()))
            edit_btn.setDisabled(True)
            delete_btn.setDisabled(False)

        def delete():
            confirm = QMessageBox.question(self, "Confirm", f"Delete subaccount {name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                del self.api_data[exchange][name]
                self.save_api_keys()
                self.active_edit = None
                self.render_exchange_sections()
                if self.on_exchanges_updated:
                    self.on_exchanges_updated()

        layout.addRow("Subaccount Name:", name_input)
        layout.addRow("API Key:", key_input)
        layout.addRow("API Secret:", secret_input)

        btn_row = QHBoxLayout()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        layout.addRow(btn_row)

        name_input.setDisabled(not is_new)
        key_input.setDisabled(not is_new)
        secret_input.setDisabled(not is_new)
        save_btn.setDisabled(not is_new)
        edit_btn.setVisible(not is_new)

        save_btn.clicked.connect(save)
        edit_btn.clicked.connect(edit)
        delete_btn.clicked.connect(delete)

        parent_box.add_widget(group)
