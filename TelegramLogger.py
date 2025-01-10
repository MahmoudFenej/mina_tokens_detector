import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
BOT_TOKEN = "7640107342:AAFHfluUgH8VeQ5GdhEvTkS-xlvVhAxYWW8"

class TelegramLogger:
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


    def sendMessageLog(self, message):
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
