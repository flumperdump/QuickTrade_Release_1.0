from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

class ExchangeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange = exchange_name

        # Main layout with no top margin
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.setLayout(layout)

        # Top controls layout
        self.top_controls = QHBoxLayout()
        self.top_controls.setSpacing(6)

        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        self.top_controls.addWidget(self.market_selector)

        self.order_type_selector = QComboBox()
        self.order_type_selector.addItems(["Market", "Limit"])
        self.order_type_selector.currentTextChanged.connect(self.toggle_price_input)
        self.top_controls.addWidget(self.order_type_selector)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.top_controls.addWidget(self.price_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.top_controls.addWidget(self.amount_input)

        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(lambda: self.place_order("Buy"))
        self.top_controls.addWidget(self.buy_button)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(lambda: self.place_order("Sell"))
        self.top_controls.addWidget(self.sell_button)

        # Add top controls directly at the top
        layout.addLayout(self.top_controls)

        # Filler to push everything to the top
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Initial toggle state
        self.toggle_price_input("Market")

    def toggle_price_input(self, order_type):
        self.price_input.setVisible(order_type == "Limit")

    def place_order(self, side):
        pair = self.market_selector.currentText()
        order_type = self.order_type_selector.currentText()
        price = self.price_input.text() if order_type == "Limit" else "Market"
        amount = self.amount_input.text()

        if order_type == "Limit" and not price:
            QMessageBox.warning(self, "Input Error", "Please enter a price for limit orders.")
            return

        if not amount:
            QMessageBox.warning(self, "Input Error", "Please enter an amount.")
            return

        QMessageBox.information(
            self,
            f"{side} Order",
            f"{side}ing {amount} of {pair} as a {order_type} order on {self.exchange}."
        )
