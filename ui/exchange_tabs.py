# ui/exchange_tabs.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QMessageBox

class ExchangeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        layout.addWidget(self.market_selector)

        self.order_type = QComboBox()
        self.order_type.addItems(["Market", "Limit"])
        layout.addWidget(self.order_type)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price (Limit Only)")
        layout.addWidget(self.price_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        layout.addWidget(self.amount_input)

        button_layout = QHBoxLayout()
        buy_button = QPushButton("Buy")
        sell_button = QPushButton("Sell")
        buy_button.clicked.connect(lambda: self.execute_order("Buy"))
        sell_button.clicked.connect(lambda: self.execute_order("Sell"))
        button_layout.addWidget(buy_button)
        button_layout.addWidget(sell_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def execute_order(self, side):
        QMessageBox.information(self, "Order Submitted", f"{side} order submitted on {self.exchange_name}")
