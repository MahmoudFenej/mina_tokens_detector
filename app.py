from flask import Flask, request, jsonify
from telethon import TelegramClient, events
import asyncio
import re
import os
import time
from datetime import datetime
import TelegramReport
import PriceChecker
import TelegramLogger
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

# Flask app
app = Flask(__name__)

# Telegram client configuration
api_id = os.getenv("TELEGRAM_API_ID", '26844985')
api_hash = os.getenv("TELEGRAM_API_HASH", 'db202faf086c8e0ad4f155b6e4c2eaf5')
report_sender = TelegramReport.TelegramReport()
logger = TelegramLogger.TelegramLogger()
checker = PriceChecker.PriceChecker()

client = TelegramClient('session_name', api_id, api_hash, proxy=None)
ADDRESS_REGEX = re.compile(r'\b[A-HJ-NP-Za-km-z1-9]{43,44}\b')

initial_investment = float(os.getenv("SOLANA_AMOUNT", "0"))
fee_per_transaction = 0.4
total_profit = 0.0

def extract_address(message_text):
    match = ADDRESS_REGEX.search(message_text)
    if match:
        return match.group(0)
    return None

def process_token(selected_token):
    global total_profit
    try:
        processed_symbols = []
        total_time_minutes = 0

        logger.sendMessageLog(f"Processing token: {selected_token}")

        initial_price = checker.fetch_price(selected_token)
        if initial_price is None:
            logger.sendMessageLog("Could not fetch the initial price.")
            return

        cumulative_percentage = 0.0
        unchanged_count = 0
        last_price = initial_price

        while True:
            time.sleep(1)
            current_price = checker.fetch_price(selected_token)

            if current_price is None:
                logger.sendMessageLog("Failed to fetch the current price. Skipping iteration.")
                continue

            percentage_change_from_initial = ((current_price - initial_price) / initial_price) * 100
            percentage_change_from_last = ((current_price - last_price) / last_price) * 100

            if percentage_change_from_last >= 1:
                logger.sendMessageLog("Buying token...")
                break

            if abs(percentage_change_from_initial) >= 60:
                logger.sendMessageLog("Significant price drop detected.")
                return

            last_price = current_price
            cumulative_percentage += percentage_change_from_last

        # buyerManager = BuyerManager.BuyerManager(selected_token)
        # buyerManager.perform_swap()

        profit = checker.track_price_change(selected_token, initial_investment)
        total_profit += (profit - fee_per_transaction)
        processed_symbols.append({'tokenSymbol': selected_token, 'profit': profit - fee_per_transaction})

        report_sender.sendReport(processed_symbols, total_time_minutes, initial_investment)

    except Exception as e:
        logger.sendMessageLog(f"Error processing token {selected_token}: {e}")

@app.route('/process-message', methods=['POST'])
def process_message():
    data = request.json
    message_text = data.get('message_text')
    message_time = datetime.fromisoformat(data.get('message_time'))
    current_time = datetime.now()
    time_diff = (current_time - message_time).total_seconds()

    if time_diff <= 30:
        selected_token = extract_address(message_text)
        if selected_token:
            process_token(selected_token)
            return jsonify({"status": "success", "message": "Token processed."})
    return jsonify({"status": "failed", "message": "Message too old or no token found."})


@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Hello"})

@app.route('/start-bot', methods=['GET'])
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def bot_listener():
        @client.on(events.NewMessage(chats='signalsolanaby4am'))
        async def handler(event):
            message_text = event.message.message
            message_time = event.message.date 
            current_time = datetime.now()
            time_diff = current_time.timestamp() - message_time.timestamp()
            
            logger.sendMessageLog(f"New Message Received ${message_time}")

            if time_diff <= 30:
                selected_token = extract_address(message_text)
                if selected_token:
                    print(f"New token detected: {selected_token}")
                    process_token(selected_token)
            else:
                logger.sendMessageLog(f"Message Dropped time diff {time_diff}")

        await client.start()
        logger.sendMessageLog("Listening for new messages...")
        await client.run_until_disconnected()

    # Run the bot listener in the background
    def run_in_background():
        loop.run_until_complete(bot_listener())

    import threading
    bot_thread = threading.Thread(target=run_in_background, daemon=True)
    bot_thread.start()

    return jsonify({"status": "bot started"})