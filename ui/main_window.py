from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.dashboard import DashboardTab
from ui.settings import SettingsTab
from ui.exchange_tabs import create_exchange_tabs
from core.data_store import load_enabled_exchanges

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1024, 650)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = DashboardTab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        self.exchange_tabs = {}
        self.init_exchange_tabs()

        self.settings_tab = SettingsTab(on_exchanges_updated=self.refresh_exchanges)
        self.tabs.addTab(self.settings_tab, "Settings")

    def init_exchange_tabs(self):
        exchanges = load_enabled_exchanges()
        for ex, tab in create_exchange_tabs(exchanges).items():
            self.exchange_tabs[ex] = tab
            self.tabs.addTab(tab, ex)

    def refresh_exchanges(self):
        for ex in list(self.exchange_tabs):
            index = self.tabs.indexOf(self.exchange_tabs[ex])
            if index != -1:
                self.tabs.removeTab(index)
        self.exchange_tabs.clear()
        self.init_exchange_tabs()
