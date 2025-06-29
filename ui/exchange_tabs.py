from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class ExchangeTab(QWidget):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange = exchange_name
        self.setLayout(QVBoxLayout())

        # Controls at the top
        controls_layout = QHBoxLayout()

        self.market_selector = QComboBox()
        self.market_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        controls_layout.addWidget(self.market_selector)

        self.order_type_selector = QComboBox()
        self.order_type_selector.addItems(["Market", "Limit"])
        self.order_type_selector.currentTextChanged.connect(self.toggle_price_input)
        controls_layout.addWidget(self.order_type_selector)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        controls_layout.addWidget(self.price_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        controls_layout.addWidget(self.amount_input)

        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(lambda: self.place_order("Buy"))
        controls_layout.addWidget(self.buy_button)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(lambda: self.place_order("Sell"))
        controls_layout.addWidget(self.sell_button)

        self.layout().addLayout(controls_layout)

        # Hide price input initially if Market order
        self.toggle_price_input(self.order_type_selector.currentText())

    def toggle_price_input(self, order_type):
        self.price_input.setVisible(order_type == "Limit")

    def place_order(self, side):
        pair = self.market_selector.currentText()
        order_type = self.order_type_selector.currentText()
        amount = self.amount_input.text().strip()
        price = self.price_input.text().strip()

        if not amount:
            QMessageBox.warning(self, "Input Error", "Amount is required.")
            return

        if order_type == "Limit" and not price:
            QMessageBox.warning(self, "Input Error", "Price is required for limit orders.")
            return

        QMessageBox.information(
            self,
            f"{side} Order",
            f"{side}ing {amount} {pair} as a {order_type} order on {self.exchange}."
        )

# This creates a dictionary of exchange_name: tab_instance
def create_exchange_tabs(exchanges):
    return {ex: ExchangeTab(ex) for ex in exchanges}
