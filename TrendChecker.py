import numpy as np
import requests
from datetime import datetime, timedelta

class TrendChecker:
    def __init__(self, address):
        self.data = self.fetch_data(address)

    def fetch_data(self, address):
        url = "https://www.okx.com/priapi/v5/dex/token/market/dex-token-hlc-candles"

        current_time = datetime.now()
        t = current_time - timedelta(seconds=30)

        params = {
            "chainId": 501,
            "address": address,
            "t": t,
            "bar": "1s",
            "limit": 47  
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch data from API")

    def extract_prices(self):
        prices = []
        for candle in self.data['data']:
            if len(candle) >= 4:
                try:
                    close_price = float(candle[3])
                    prices.append(close_price)
                except ValueError:
                    print(f"Skipping invalid close price data: {candle[3]}")
                    continue
            else:
                print(f"Skipping malformed candle: {candle}")
                continue
        return prices

    def average_prices(self, prices):
        split_index = len(prices) // 2
        first_half = prices[:split_index]
        second_half = prices[split_index:]
        
        avg_first_half = np.mean(first_half)
        avg_second_half = np.mean(second_half)
        
        return avg_first_half, avg_second_half

    def check_trend(self):
        prices = self.extract_prices()

        if len(prices) < 2:
            return {"error": "Not enough data for trend analysis"}

        avg_first_half, avg_second_half = self.average_prices(prices)

        trend_is_increasing = avg_second_half > avg_first_half

        return {
            'is_increasing': trend_is_increasing,
            'first_half_avg': avg_first_half,
            'second_half_avg': avg_second_half
        }

