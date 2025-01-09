import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

BOT_TOKEN = "7750444311:AAFyeiTLM-ZFZ0XfyoADVc7W8zOBZKKtO84"

class TelegramReport:
    def __init__(self):
        self.chat_ids = self.get_chat_ids()

    def get_chat_ids(self):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        data = response.json()

        chat_ids = set()
        if response.status_code == 200 and data.get("result"):
             for entry in data["result"]:
                if "message" in entry and "chat" in entry["message"]:
                    chat_ids.add(entry["message"]["chat"]["id"])  # Add chat ID to the set
        else:
            print("Failed to retrieve chat IDs. Ensure users have sent a message to your bot.")
        return chat_ids

    def sendReport(self, processed_symbols, total_time_minutes, initial_investment):
        sumofpositive = [
            {"profit": symbol.get("profit", 0), "tokenSymbol": symbol["tokenSymbol"]}
            for symbol in processed_symbols if symbol.get("profit", 0) > 0
        ]
        sumofnegative = [
            {"profit": symbol.get("profit", 0), "tokenSymbol": symbol["tokenSymbol"]}
            for symbol in processed_symbols if symbol.get("profit", 0) < 0
        ]
       
        skipped_tokens = sum(1 for symbol in processed_symbols if "profit" not in symbol)

        total_positive_profit = sum(entry["profit"] for entry in sumofpositive)
        total_negative_profit = sum(entry["profit"] for entry in sumofnegative)
        total_profit = total_negative_profit + total_positive_profit
        total_all_transactions = len(processed_symbols)

        # Determine the maximum width for token symbols and profits for alignment
        max_token_length = max(len(entry["tokenSymbol"]) for entry in processed_symbols)
        max_profit_length = max(len(f"${entry.get('profit', 0):.2f}") for entry in processed_symbols)

        positive_table = ",".join([ 
            f" {entry['tokenSymbol'].ljust(max_token_length)} => {('${:0.2f}'.format(entry.get('profit', 0))).rjust(max_profit_length)} "
            for entry in sumofpositive
        ])

        negative_table = ",".join([ 
            f"  {entry['tokenSymbol'].ljust(max_token_length)} => {('${:0.2f}'.format(entry.get('profit', 0))).rjust(max_profit_length)} "
            for entry in sumofnegative
        ])

        report = f"""
                --- Report ---

        **Investment**: {initial_investment} **Take Profit %**: { os.getenv("INCREASE_RATIO")} **Stop Loose %**: { os.getenv("DECREASE_RATIO")}

        **Positive Profits**:
        |{'-' * (max_token_length + max_profit_length + 5)}|
        {positive_table}

        **Negative Profits**:
        |{'-' * (max_token_length + max_profit_length + 5)}|
        {negative_table}

        **Summary**:
        - Total Time Taken: {total_time_minutes:.2f} minutes
        - count of All Transactions: {total_all_transactions}
        - count Skipped Tokens: {skipped_tokens}

        - ✅ Total Positive Profit:  ${total_positive_profit:.2f}
        - ❌ Total Negative Profit:  ${total_negative_profit:.2f}
        -    Total Profit: ${total_profit:.2f}
        """

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chat_id in self.chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": report
            }

            response = requests.post(url, data=payload)

            if response.status_code == 200:
                print(f"Report sent to chat ID {chat_id} successfully!")
            else:
                print(f"Failed to send report to chat ID {chat_id}. Error: {response.text}")

    def sendMessageReport(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{message}\nCurrent Time: {current_time}")
        time_report = f"{message}\nCurrent Time: {current_time}"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        for chat_id in self.chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": time_report
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"Time report sent to chat ID {chat_id} successfully!")
            else:
                print(f"Failed to send time report to chat ID {chat_id}. Error: {response.text}")

if __name__ == "__main__":
    BOT_TOKEN = "7750444311:AAFyeiTLM-ZFZ0XfyoADVc7W8zOBZKKtO84"
    
    processed_symbols = [
        {"profit": 10, "tokenSymbol": "BTC"},
        {"profit": -5, "tokenSymbol": "ETH"},
        {"profit": -5, "tokenSymbol": "xxx"},
        {"profit": -10, "tokenSymbol": "TEST"},
        {"tokenSymbol": "DOGE"},
        {"profit": 0, "tokenSymbol": "XRP"}
    ]
    total_time_minutes = 12.5
    address = "0x1234567890abcdef"

    report_sender = TelegramReport(BOT_TOKEN)
    report_sender.sendReport(processed_symbols, total_time_minutes, 30)
    report_sender.sendMessageReport(address)
