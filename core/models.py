# core/models.py

from dataclasses import dataclass

@dataclass
class TradeRequest:
    exchange: str
    subaccount: str
    symbol: str
    side: str  # "Buy" or "Sell"
    amount: float
    order_type: str  # "Market" or "Limit"
    price: float = None
