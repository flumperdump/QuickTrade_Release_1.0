import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton,
    QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

API_KEYS_PATH = "config/api_keys.json"


class ExchangeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange = exchange_name

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 12, 10, 10)
        self.layout().setSpacing(8)

        # Row 1: Subaccount selector & Trading pair
        row1 = QHBoxLayout()
        self.subaccount_selector = QComboBox()
        self.load_subaccounts()
        row1.addWidget(self.subaccount_selector)

        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        row1.addWidget(self.market_selector)
        self.layout().addLayout(row1)

        # Row 2: Order type, Price, Amount
        row2 = QHBoxLayout()
        self.order_type_selector = QComboBox()
        self.order_type_selector.addItems(["Market", "Limit"])
        self.order_type_selector.currentTextChanged.connect(self.toggle_price_input)
        row2.addWidget(self.order_type_selector)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        row2.addWidget(self.price_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        row2.addWidget(self.amount_input)
        self.layout().addLayout(row2)

        # Row 3: Buy & Sell buttons
        row3 = QHBoxLayout()
        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(lambda: self.place_order("Buy"))
        row3.addWidget(self.buy_button)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(lambda: self.place_order("Sell"))
        row3.addWidget(self.sell_button)

        self.layout().addLayout(row3)

        # Spacer to push content up
        self.layout().addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Default state
        self.toggle_price_input("Market")

    def load_subaccounts(self):
        self.subaccount_selector.clear()
        try:
            with open(API_KEYS_PATH, 'r') as f:
                api_keys = json.load(f)
            subs = api_keys.get(self.exchange, {})
            if subs:
                self.subaccount_selector.addItems(list(subs.keys()))
            else:
                self.subaccount_selector.addItem("Default")
        except Exception as e:
            self.subaccount_selector.addItem("Default")

    def toggle_price_input(self, order_type):
        self.price_input.setVisible(order_type == "Limit")

    def place_order(self, side):
        subaccount = self.subaccount_selector.currentText()
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
            f"{side}ing {amount} of {pair} as a {order_type} order "
            f"on {self.exchange} using subaccount {subaccount}."
        )


def create_exchange_tabs(exchange_names):
    return {name: ExchangeTab(name) for name in exchange_names}
