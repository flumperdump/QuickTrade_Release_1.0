# ui/exchange_tabs.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from core.trade_executor import TradeExecutor

executor = TradeExecutor()

def create_exchange_tabs(selected_exchanges):
    tabs = {}

    for exchange in selected_exchanges:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel(f"{exchange} Trading Interface"))

        pair_selector = QComboBox()
        pair_selector.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        layout.addWidget(pair_selector)

        order_type = QComboBox()
        order_type.addItems(["Market", "Limit"])
        layout.addWidget(order_type)

        price_input = QLineEdit()
        price_input.setPlaceholderText("Price (Limit only)")
        layout.addWidget(price_input)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Amount")
        layout.addWidget(amount_input)

        button_layout = QHBoxLayout()
        buy_button = QPushButton("Buy")
        sell_button = QPushButton("Sell")
        button_layout.addWidget(buy_button)
        button_layout.addWidget(sell_button)
        layout.addLayout(button_layout)

        def handle_trade(side):
            symbol = pair_selector.currentText()
            typ = order_type.currentText()
            price = price_input.text() if typ == "Limit" else None
            amount = amount_input.text()

            executor.place_order(
                parent_widget=tab,
                exchange=exchange,
                subaccount="Main",  # Placeholder
                symbol=symbol,
                side=side,
                amount=amount,
                order_type=typ,
                price=price
            )

        buy_button.clicked.connect(lambda: handle_trade("Buy"))
        sell_button.clicked.connect(lambda: handle_trade("Sell"))

        tabs[exchange] = tab

    return tabs
