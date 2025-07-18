from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
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

        layout.addWidget(QLabel("Confirm?"))
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
        self.toggle_button.setToolButtonStyle(QToolButton.ToolButtonStyle.ToolButtonTextBesideIcon)
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
        self.setLayout(self.main_layout)

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
        self.active_edit = None

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

        QTimer.singleShot(0, self.render_exchange_sections)

    def set_controls_enabled(self, enabled):
        self.choose_btn.setEnabled(enabled)
        for i in range(self.api_layout.count()):
            box = self.api_layout.itemAt(i).widget()
            if isinstance(box, CollapsibleBox):
                if enabled:
                    box.unlock_toggle()
                else:
                    box.lock_toggle()

    def render_exchange_sections(self):
        for i in reversed(range(self.api_layout.count())):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for ex in self.selected_exchanges:
            exchange_box = CollapsibleBox(ex)
            subaccounts = self.api_data.get(ex, {})

            for subaccount, creds in subaccounts.items():
                self.build_subaccount_ui(exchange_box, ex, subaccount, creds)

            add_sub_btn = QPushButton(f"Add Subaccount to {ex}")
            add_sub_btn.setMinimumHeight(28)
            add_sub_btn.setMinimumWidth(180)
            add_sub_btn.clicked.connect(lambda _, e=ex: self.add_subaccount(e))
            add_sub_btn.setEnabled(self.active_edit is None)
            exchange_box.add_widget(add_sub_btn)
            self.api_layout.addWidget(exchange_box)

        # Only call the callback if it exists and is not None
        if callable(self.on_exchanges_updated):
            self.on_exchanges_updated()

    def build_subaccount_ui(self, container, exchange, subaccount, creds):
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

        def save():
            new_sub = sub_name_input.text().strip()
            key = api_key_input.text().strip()
            secret = api_secret_input.text().strip()
            if not new_sub or not key or not secret:
                return

            if new_sub != subaccount:
                self.api_data[exchange].pop(subaccount, None)
            self.api_data[exchange][new_sub] = {"api_key": key, "api_secret": secret}
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(self.api_data, f, indent=2)

            if "subaccount_settings" not in self.user_prefs:
                self.user_prefs["subaccount_settings"] = {}
            if exchange not in self.user_prefs["subaccount_settings"]:
                self.user_prefs["subaccount_settings"][exchange] = {}
            if new_sub not in self.user_prefs["subaccount_settings"][exchange]:
                self.user_prefs["subaccount_settings"][exchange][new_sub] = {
                    "last_pair": "BTC/USDT"
                }
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.user_prefs, f, indent=2)

            self.active_edit = None
            self.set_controls_enabled(True)
            self.render_exchange_sections()

        def edit():
            self.active_edit = (exchange, subaccount)
            self.set_controls_enabled(False)
            sub_name_input.setDisabled(False)
            api_key_input.setDisabled(False)
            api_secret_input.setDisabled(False)
            save_btn.setDisabled(False)
            edit_btn.setVisible(False)

        def delete():
            confirm = QMessageBox.question(
                self, "Delete Subaccount?",
                f"Are you sure you want to delete {subaccount}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                if exchange in self.api_data and subaccount in self.api_data[exchange]:
                    del self.api_data[exchange][subaccount]
                    with open(API_KEYS_PATH, 'w') as f:
                        json.dump(self.api_data, f, indent=2)
                    self.active_edit = None
                    self.set_controls_enabled(True)
                    self.render_exchange_sections()

        is_new = creds["api_key"] == "" and creds["api_secret"] == ""
        if is_new:
            edit_btn.setVisible(False)
            sub_name_input.setDisabled(False)
            api_key_input.setDisabled(False)
            api_secret_input.setDisabled(False)
            self.active_edit = (exchange, subaccount)
            self.set_controls_enabled(False)
        else:
            sub_name_input.setDisabled(True)
            api_key_input.setDisabled(True)
            api_secret_input.setDisabled(True)
            save_btn.setDisabled(True)
            edit_btn.clicked.connect(edit)

        save_btn.clicked.connect(save)
        delete_btn.clicked.connect(delete)

        row = QHBoxLayout()
        row.addWidget(save_btn)
        row.addWidget(edit_btn)
        row.addWidget(delete_btn)
        row.addStretch()

        sub_box.layout().addRow("Subaccount Name:", sub_name_input)
        sub_box.layout().addRow("API Key:", api_key_input)
        sub_box.layout().addRow("API Secret:", api_secret_input)
        sub_box.layout().addRow(row)

        container.add_widget(sub_box)

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.selected_exchanges)
        if dialog.exec():
            selected = dialog.get_selected()
            self.selected_exchanges = selected
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({"enabled_exchanges": selected}, f, indent=2)
            self.render_exchange_sections()

    def add_subaccount(self, exchange):
        if self.active_edit is not None:
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
