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
        self.exchange_tabs = {}  # FIX: Must be defined before settings
        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)
        self.refresh_exchanges()

        self.tabs.insertTab(0, self.dashboard_tab, "Dashboard")
        self.tabs.insertTab(999, self.settings, "Settings")  # Always last
        self.tabs.setCurrentIndex(0)

    def refresh_exchanges(self):
        for name, tab in self.exchange_tabs.items():
            index = self.tabs.indexOf(tab)
            if index != -1:
                self.tabs.removeTab(index)
        self.exchange_tabs.clear()

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                enabled_exchanges = config.get("enabled_exchanges", [])
        else:
            enabled_exchanges = []

        for ex in enabled_exchanges:
            tab = ExchangeTab(ex)
            self.exchange_tabs[ex] = tab
            self.tabs.insertTab(1, tab, ex)

# ✅ Standalone run function
def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# ✅ Entry point
if __name__ == "__main__":
    run_app()
