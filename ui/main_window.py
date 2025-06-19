from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.dashboard import DashboardTab
from ui.settings import SettingsTab
from ui.exchange_tabs import create_exchange_tabs
from core.data_store import load_enabled_exchanges
from PyQt6.QtWidgets import QApplication
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1100, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard = DashboardTab()
        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)

        self.exchange_tabs = {}
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.load_exchange_tabs()
        self.tabs.addTab(self.settings, "Settings")
        self.tabs.setCurrentIndex(0)

    def load_exchange_tabs(self):
        enabled = load_enabled_exchanges()
        self.exchange_tabs = create_exchange_tabs(enabled)
        for name, tab in self.exchange_tabs.items():
            self.tabs.addTab(tab, name)

    def refresh_exchanges(self):
        for name in list(self.exchange_tabs):
            index = self.tabs.indexOf(self.exchange_tabs[name])
            if index != -1:
                self.tabs.removeTab(index)
        self.load_exchange_tabs()


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
