from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
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
        self.resize(1024, 650)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard = DashboardTab()
        self.tabs.addTab(self.dashboard, "Dashboard")

        self.exchange_tabs = {}
        self.load_enabled_exchanges()

        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)
        self.tabs.addTab(self.settings, "Settings")

        self.tabs.setCurrentIndex(0)

    def load_enabled_exchanges(self):
        self.enabled_exchanges = []
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                self.enabled_exchanges = config.get("enabled_exchanges", [])

        for name in self.enabled_exchanges:
            if name not in self.exchange_tabs:
                tab = ExchangeTab(name)
                self.exchange_tabs[name] = tab
                self.tabs.insertTab(self.tabs.count() - 1, tab, name)

    def refresh_exchanges(self):
        for name, tab in self.exchange_tabs.items():
            self.tabs.removeTab(self.tabs.indexOf(tab))
        self.exchange_tabs.clear()
        self.load_enabled_exchanges()

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
