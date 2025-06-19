# models.py

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class APICredentials:
    """Holds the API credentials for a subaccount."""
    api_key: str
    api_secret: str


@dataclass
class SubAccount:
    """Represents a subaccount within an exchange."""
    name: str
    credentials: APICredentials


@dataclass
class ExchangeConfig:
    """Represents the API configuration for an exchange."""
    name: str
    subaccounts: Dict[str, SubAccount] = field(default_factory=dict)


@dataclass
class UserPreferences:
    """Stores user-level preferences that persist across sessions."""
    enabled_exchanges: List[str] = field(default_factory=list)
    display_currency: str = "USD"
    show_dust: bool = False
    theme: str = "dark"  # options: "dark", "light"
