from PyQt6.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QuickTrade Dashboard')
        self.setGeometry(100, 100, 800, 600)
        self.setCentralWidget(QLabel('Welcome to QuickTrade'))
