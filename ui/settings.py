from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QGroupBox, QToolButton, QSizePolicy, QFrame, QSpacerItem,
    QCheckBox
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

        layout.addWidget(QLabel("Confirm?"))
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

        self.choose_btn.clicked.connect(self.choose_exchanges)
        self.render_exchange_sections()

    def choose_exchanges(self):
        dialog = ExchangeSelectionDialog(self.user_prefs.get("enabled_exchanges", []))
        if dialog.exec():
            selected = dialog.get_selected()
            self.user_prefs["enabled_exchanges"] = selected
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.user_prefs, f, indent=2)
            self.render_exchange_sections()
            self.active_add = False
            self.active_editing = None

    def add_subaccount(self, exchange):
        if self.active_add:
            return
        subaccount = f"Sub{len(self.api_data.get(exchange, {})) + 1}"
        if exchange not in self.api_data:
            self.api_data[exchange] = {}
        self.api_data[exchange][subaccount] = {"api_key": "", "api_secret": ""}
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(self.api_data, f, indent=2)
        self.active_add = True
        self.active_editing = (exchange, subaccount)
        self.render_exchange_sections()

    def render_exchange_sections(self):
        for i in reversed(range(self.api_layout.count())):
            widget = self.api_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for ex in self.user_prefs.get("enabled_exchanges", []):
            exchange_box = CollapsibleBox(ex)
            if self.active_add or self.active_editing:
                exchange_box.toggle_button.setEnabled(False)

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

                is_new = creds["api_key"] == "" and creds["api_secret"] == ""
                is_editing = self.active_editing == (ex, subaccount)

                should_disable = self.active_add and not is_editing
                if should_disable:
                    save_btn.setDisabled(True)
                    edit_btn.setDisabled(True)
                    delete_btn.setDisabled(True)
                    for field in (sub_name_input, api_key_input, api_secret_input):
                        field.setDisabled(True)

                if is_new or is_editing:
                    edit_btn.setVisible(False)
                    self.active_add = True
                    self.set_controls_enabled(False)
                else:
                    sub_name_input.setDisabled(True)
                    api_key_input.setDisabled(True)
                    api_secret_input.setDisabled(True)
                    save_btn.setDisabled(True)
                    edit_btn.clicked.connect(self.make_edit_func(
                        sub_name_input, api_key_input, api_secret_input,
                        save_btn, edit_btn, ex, subaccount
                    ))

                save_btn.clicked.connect(self.make_save_func(
                    ex, subaccount, sub_name_input, api_key_input, api_secret_input,
                    save_btn, edit_btn
                ))
                delete_btn.clicked.connect(self.make_delete_func(ex, subaccount))

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

    def make_save_func(self, ex, old_sub, name_input, k, s, save_btn, edit_btn):
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
            self.active_editing = None
            self.set_controls_enabled(True)
            self.render_exchange_sections()
        return save

    def make_edit_func(self, name_input, k, s, save_btn, edit_btn, ex, subaccount):
        def edit():
            name_input.setDisabled(False)
            k.setDisabled(False)
            s.setDisabled(False)
            save_btn.setDisabled(False)
            edit_btn.setVisible(False)
            self.active_add = True
            self.active_editing = (ex, subaccount)
            self.set_controls_enabled(False)
            self.render_exchange_sections()
        return edit

    def make_delete_func(self, ex, sub):
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
                    self.active_editing = None
                    self.set_controls_enabled(True)
                    self.render_exchange_sections()
        return delete

    def set_controls_enabled(self, enabled):
        self.choose_btn.setEnabled(enabled)
        for i in range(self.api_layout.count()):
            box = self.api_layout.itemAt(i).widget()
            if isinstance(box, CollapsibleBox):
                if enabled:
                    box.unlock_toggle()
                else:
                    box.lock_toggle()
