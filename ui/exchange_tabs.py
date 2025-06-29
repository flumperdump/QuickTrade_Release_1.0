from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
import json
import os

CONFIG_PATH = "config"
API_KEYS_FILE = os.path.join(CONFIG_PATH, "api_keys.json")

class ExchangeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange = exchange_name

        # Main layout with margin for top spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 10, 5, 5)
        layout.setSpacing(6)
        self.setLayout(layout)

        # Load subaccounts for this exchange
        self.subaccount_selector = QComboBox()
        self.load_subaccounts()

        # Set up auto-refresh of subaccount list
        self.last_subaccounts = []
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.check_subaccount_updates)
        self.refresh_timer.start(2000)  # Check every 2 seconds

        # Line 1: Subaccount and Trading Pair
        top_row = QHBoxLayout()
        top_row.addWidget(self.subaccount_selector)

        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        top_row.addWidget(self.market_selector)
        layout.addLayout(top_row)

        # Line 2: Order Type, Price (if Limit), and Amount
        mid_row = QHBoxLayout()

        self.order_type_selector = QComboBox()
        self.order_type_selector.addItems(["Market", "Limit"])
        self.order_type_selector.currentTextChanged.connect(self.toggle_price_input)
        mid_row.addWidget(self.order_type_selector)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        mid_row.addWidget(self.price_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        mid_row.addWidget(self.amount_input)

        layout.addLayout(mid_row)

        # Line 3: Buy/Sell Buttons
        btn_row = QHBoxLayout()
        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(lambda: self.place_order("Buy"))
        btn_row.addWidget(self.buy_button)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(lambda: self.place_order("Sell"))
        btn_row.addWidget(self.sell_button)

        layout.addLayout(btn_row)

        # Spacer to push everything to the top
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Initial toggle state
        self.toggle_price_input("Market")

    def toggle_price_input(self, order_type):
        self.price_input.setVisible(order_type == "Limit")

    def load_subaccounts(self):
        self.subaccount_selector.clear()
        subaccounts = []
        if os.path.exists(API_KEYS_FILE):
            try:
                with open(API_KEYS_FILE, 'r') as f:
                    api_data = json.load(f)
                    subaccounts = list(api_data.get(self.exchange, {}).keys())
                    self.subaccount_selector.addItems(subaccounts)
            except Exception as e:
                print(f"Error loading API keys: {e}")
        self.last_subaccounts = subaccounts

    def check_subaccount_updates(self):
        if os.path.exists(API_KEYS_FILE):
            try:
                with open(API_KEYS_FILE, 'r') as f:
                    api_data = json.load(f)
                    current_subs = list(api_data.get(self.exchange, {}).keys())
                    if current_subs != self.last_subaccounts:
                        self.subaccount_selector.clear()
                        self.subaccount_selector.addItems(current_subs)
                        self.last_subaccounts = current_subs
            except Exception as e:
                print(f"Error checking subaccount updates: {e}")

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
            f"{side}ing {amount} of {pair} as a {order_type} order on {self.exchange} ({subaccount})."
        )
