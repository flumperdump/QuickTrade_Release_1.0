# price fetcher logic placeholder
# price_fetcher.py

import requests
import time

class PriceFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # seconds
        self.last_fetch_time = {}

    def get_price(self, base: str, quote: str = "usd") -> float:
        """
        Fetches the price of a crypto asset in the desired quote currency.
        Uses a simple cache to avoid API rate-limiting issues.
        """
        symbol = f"{base.lower()}_{quote.lower()}"

        current_time = time.time()
        if symbol in self.cache and current_time - self.last_fetch_time[symbol] < self.cache_duration:
            return self.cache[symbol]

        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={base.lower()}&vs_currencies={quote.lower()}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            price = data[base.lower()][quote.lower()]
            self.cache[symbol] = price
            self.last_fetch_time[symbol] = current_time
            return price
        except Exception as e:
            print(f"[PriceFetcher] Failed to fetch price for {base}/{quote}: {e}")
            return 0.0
