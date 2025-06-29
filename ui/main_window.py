from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from ui.dashboard import DashboardTab
from ui.settings import SettingsTab
from ui.exchange_tabs import create_exchange_tabs
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTrade")
        self.resize(1080, 720)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Dashboard Tab always first
        self.dashboard_tab = DashboardTab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Exchange Tabs placeholder
        self.exchange_tabs = {}
        self.load_exchange_tabs()

        # Settings Tab always last
        self.settings = SettingsTab(on_exchanges_updated=self.refresh_exchanges)
        self.tabs.addTab(self.settings, "Settings")

        # Default to Dashboard
        self.tabs.setCurrentIndex(0)

    def load_exchange_tabs(self):
        for name, widget in create_exchange_tabs():
            self.exchange_tabs[name] = widget
            self.tabs.insertTab(self.tabs.count() - 1, widget, name)

    def refresh_exchanges(self):
        # Remove old exchange tabs
        for name, widget in self.exchange_tabs.items():
            index = self.tabs.indexOf(widget)
            if index != -1:
                self.tabs.removeTab(index)

        # Reload new ones
        self.exchange_tabs = {}
        self.load_exchange_tabs()

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
