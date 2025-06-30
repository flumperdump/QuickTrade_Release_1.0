from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget
from ui.dashboard import DashboardTab
from ui.settings import SettingsTab
from ui.exchange_tabs import ExchangeTab
import sys
import json
import os

CONFIG_PATH = "config/user_prefs.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1000, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = DashboardTab()
        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)

        # Load exchanges from user preferences
        self.exchange_tabs = {}
        self.refresh_exchanges()

        # Add Dashboard first, then exchanges, then settings
        self.tabs.insertTab(0, self.dashboard_tab, "Dashboard")
        self.tabs.insertTab(999, self.settings, "Settings")  # Will always go last

        self.tabs.setCurrentIndex(0)

    def refresh_exchanges(self):
        # Remove all current exchange tabs
        for name, tab in self.exchange_tabs.items():
            index = self.tabs.indexOf(tab)
            if index != -1:
                self.tabs.removeTab(index)

        self.exchange_tabs.clear()

        # Load enabled exchanges from config
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                enabled_exchanges = config.get("enabled_exchanges", [])
        else:
            enabled_exchanges = []

        # Recreate exchange tabs
        for ex in enabled_exchanges:
            tab = ExchangeTab(ex)
            self.exchange_tabs[ex] = tab
            self.tabs.insertTab(1, tab, ex)  # Insert after Dashboard

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
