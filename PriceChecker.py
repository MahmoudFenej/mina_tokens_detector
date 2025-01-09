import requests
import time
from dotenv import load_dotenv
import os
import TelegramReport

load_dotenv()

BOT_TOKEN = "7750444311:AAFyeiTLM-ZFZ0XfyoADVc7W8zOBZKKtO84"


class PriceChecker:

    def __init__(self):
        self.increase_ratio = float(os.getenv("INCREASE_RATIO", 20)) 
        self.decrease_ratio = float(os.getenv("DECREASE_RATIO", 10))

    def fetch_price(self, mint_address: str) -> float | None:
        url = f"https://data.fluxbeam.xyz/tokens/{mint_address}/price"

        try:
            response = requests.get(url, timeout=10)  # Add a timeout for the request
            response.raise_for_status()  # Raise HTTPError for bad responses
            response_data = response.json()

            if isinstance(response_data, dict):
                if 'error' in response_data:
                    print(f"Error fetching price: {response_data['error']}")
                    return None
                return response_data.get('price')

            if isinstance(response_data, (float, int)):
                return float(response_data)

            print("Unexpected response structure.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing response: {e}")
            return None

    def sell(self, current_price: float, initial_investment: float, initial_price: float, detected_token) -> None:
        coins_bought = initial_investment / initial_price
        current_value = coins_bought * current_price
        profit = current_value - initial_investment
        report_sender = TelegramReport.TelegramReport()
        report_sender.sendMessageReport("selled successfully Profit: {profit:.2f}")
        
        print(f"Sell triggered!")
        print(f"Initial price: {initial_price}, Current price: {current_price}")
        print(f"Initial investment: {initial_investment}, Coins bought: {coins_bought:.6f}")
        print(f"Current value: {current_value:.2f}, Profit: {profit:.2f}")

        # sellerManager = SellerManager.SellerManager(detected_token)
        # sellerManager.perform_swap()
        return profit

  
    def track_price_change(self, mint_address: str, initial_investment) -> None:
        initial_price = self.fetch_price(mint_address)

        if initial_price is None:
            print("Could not fetch the initial price.")
            return

        print(f"Initial price: {initial_price}")
        sell_triggered = False
        last_price = initial_price

        cumulative_percentage = 0.0
        unchanged_count = 0
        last_percentage_change = None

        while not sell_triggered:
            time.sleep(1)
            current_price = self.fetch_price(mint_address)

            if current_price is None:
                print("Failed to fetch the current price. Skipping this iteration.")
                continue

            # Percentage change compared to the last price
            percentage_change_from_initial = ((current_price - initial_price) / initial_price) * 100
            percentage_change_from_last = ((current_price - last_price) / last_price) * 100

            print(f"Percentage change from initial: {percentage_change_from_initial:.2f}%")
            print(f"Percentage change from last price: {percentage_change_from_last:.2f}%")

            # Check for unchanged percentage change
            if last_percentage_change is not None and percentage_change_from_last == last_percentage_change:
                unchanged_count += 1
            else:
                unchanged_count = 0

            last_percentage_change = percentage_change_from_last

            if unchanged_count >= 7:
                print("Percentage change from last price has remained the same for 5 iterations. Triggering sell.")
                profit = self.sell(current_price, initial_investment, initial_price, mint_address)
                sell_triggered = True
                return profit

            cumulative_percentage += percentage_change_from_last

            if percentage_change_from_initial >= self.increase_ratio:
                profit = self.sell(current_price, initial_investment, initial_price, mint_address)
                sell_triggered = True
                return profit

            if abs(percentage_change_from_initial) >= self.decrease_ratio or cumulative_percentage >= self.decrease_ratio:
                print(f"Cumulative decrease of {cumulative_percentage:.2f}% detected! Triggering sell.")
                profit = self.sell(current_price, initial_investment, initial_price, mint_address)
                sell_triggered = True
                return profit

            last_price = current_price



