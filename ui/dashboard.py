# ui/dashboard.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QHBoxLayout
import json
import os

CONFIG_PATH = "config"
USER_PREFS_FILE = os.path.join(CONFIG_PATH, "user_prefs.json")
API_KEYS_FILE = os.path.join(CONFIG_PATH, "api_keys.json")

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.total_label = QLabel("💰 Total Asset Value: USD $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout().addWidget(self.total_label)

        controls_layout = QHBoxLayout()
        self.dust_filter = QCheckBox("Show Dust (<$1)")
        self.dust_filter.setChecked(False)
        self.dust_filter.stateChanged.connect(self.update_table)

        self.refresh_button = QPushButton("🔁 Refresh Assets")
        self.refresh_button.clicked.connect(self.load_balances)

        controls_layout.addWidget(self.dust_filter)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        self.layout().addLayout(controls_layout)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Exchange", "Subaccount", "Asset", "Balance (USD)"])
        self.layout().addWidget(self.table)

        self.balances = []
        self.load_balances()

    def load_balances(self):
        # Dummy data for now
        self.balances = [
            {"exchange": "Binance", "subaccount": "Main", "asset": "BTC", "usd_value": 23450.12},
            {"exchange": "Kraken", "subaccount": "Bot1", "asset": "ETH", "usd_value": 1345.33},
            {"exchange": "KuCoin", "subaccount": "Main", "asset": "DOGE", "usd_value": 0.52},
            {"exchange": "Bybit", "subaccount": "Alt", "asset": "SOL", "usd_value": 85.22}
        ]
        self.update_table()

    def update_table(self):
        show_dust = self.dust_filter.isChecked()
        filtered = [b for b in self.balances if show_dust or b["usd_value"] >= 1.0]
        self.table.setRowCount(len(filtered))
        total = 0.0
        for i, b in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(b["exchange"]))
            self.table.setItem(i, 1, QTableWidgetItem(b["subaccount"]))
            self.table.setItem(i, 2, QTableWidgetItem(b["asset"]))
            self.table.setItem(i, 3, QTableWidgetItem(f"${b['usd_value']:.2f}"))
            total += b["usd_value"]
        self.total_label.setText(f"💰 Total Asset Value: USD ${total:,.2f}")
