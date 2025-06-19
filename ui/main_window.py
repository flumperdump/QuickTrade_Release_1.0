# ui/main_window.py

from PyQt6.QtWidgets import QApplication
import sys
from ui.dashboard import DashboardTab
from ui.exchange_tabs import create_exchange_tabs
from ui.settings import SettingsTab
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from core.data_store import load_enabled_exchanges

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1000, 680)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Load saved exchange preferences
        enabled_exchanges = load_enabled_exchanges()

        # Add dashboard
        self.dashboard_tab = DashboardTab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Add exchange tabs dynamically
        self.exchange_tabs = create_exchange_tabs(enabled_exchanges)
        for name, tab in self.exchange_tabs.items():
            self.tabs.addTab(tab, name)

        # Add settings tab
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "Settings")

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
