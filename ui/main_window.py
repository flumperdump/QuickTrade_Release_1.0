from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
import sys
import os
import json

from ui.dashboard import DashboardTab
from ui.settings import SettingsTab
from ui.exchange_tabs import ExchangeTab

CONFIG_PATH = "config"
USER_PREFS_FILE = os.path.join(CONFIG_PATH, "user_prefs.json")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1000, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Dashboard tab first
        self.dashboard = DashboardTab()
        self.tabs.addTab(self.dashboard, "Dashboard")

        # Placeholder for exchange tabs, to be populated below
        self.exchange_tabs = {}

        # Settings tab last, with callback to refresh exchanges
        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)
        self.tabs.addTab(self.settings, "Settings")

        # Initial load of exchange tabs
        self.refresh_exchanges()

        self.tabs.setCurrentIndex(0)  # Start on Dashboard

    def refresh_exchanges(self):
        # Remove all tabs between Dashboard (index 0) and Settings (last)
        while self.tabs.count() > 2:
            self.tabs.removeTab(1)

        # Load selected exchanges from config
        selected_exchanges = []
        if os.path.exists(USER_PREFS_FILE):
            try:
                with open(USER_PREFS_FILE, 'r') as f:
                    prefs = json.load(f)
                    selected_exchanges = prefs.get("enabled_exchanges", [])
            except Exception as e:
                print(f"Error loading user preferences: {e}")

        # Create new ExchangeTabs for selected exchanges
        for ex in selected_exchanges:
            tab = ExchangeTab(ex)
            self.exchange_tabs[ex] = tab
            self.tabs.insertTab(self.tabs.count() - 1, tab, ex)

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
