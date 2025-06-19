# trade_tabs.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class TradeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.setLayout(QVBoxLayout())

        # Market Selector
        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        self.layout().addWidget(QLabel("Select Pair:"))
        self.layout().addWidget(self.market_selector)

        # Order Type Selector
        self.order_type = QComboBox()
        self.order_type.addItems(["Market", "Limit"])
        self.order_type.currentTextChanged.connect(self.toggle_price_input)
        self.layout().addWidget(QLabel("Order Type:"))
        self.layout().addWidget(self.order_type)

        # Price (shown only for Limit orders)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.layout().addWidget(self.price_input)

        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.layout().addWidget(self.amount_input)

        # Buy/Sell Buttons
        btn_layout = QHBoxLayout()
        self.buy_button = QPushButton("Buy")
        self.sell_button = QPushButton("Sell")
        btn_layout.addWidget(self.buy_button)
        btn_layout.addWidget(self.sell_button)
        self.layout().addLayout(btn_layout)

        self.buy_button.clicked.connect(lambda: self.submit_order("Buy"))
        self.sell_button.clicked.connect(lambda: self.submit_order("Sell"))

        self.toggle_price_input("Market")  # Default state

    def toggle_price_input(self, order_type):
        self.price_input.setVisible(order_type == "Limit")

    def submit_order(self, side):
        pair = self.market_selector.currentText()
        order_type = self.order_type.currentText()
        price = self.price_input.text().strip()
        amount = self.amount_input.text().strip()

        if not amount:
            QMessageBox.warning(self, "Missing Input", "Please enter amount.")
            return

        if order_type == "Limit" and not price:
            QMessageBox.warning(self, "Missing Input", "Please enter price for Limit order.")
            return

        QMessageBox.information(self, f"{side} Order",
                                f"{side} {amount} {pair} as a {order_type} order on {self.exchange_name}.")
