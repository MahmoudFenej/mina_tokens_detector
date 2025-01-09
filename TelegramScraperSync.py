import re
import time
from telethon import TelegramClient, events
import TelegramReport
import PriceChecker
import RugChecker
from dotenv import load_dotenv
import os
import TelegramLogger
import random
import string

load_dotenv()

api_id = '27753991'
api_hash = 'bd527f9b3f1d56c77675f8b8e441c15f'
report_sender = TelegramReport.TelegramReport()
logger = TelegramLogger.TelegramLogger()

def generate_session_name(length=5):
    chars = string.ascii_letters + string.digits
    session_name = ''.join(random.choices(chars, k=length))
    return session_name

client = TelegramClient(generate_session_name(), api_id, api_hash)
rug_checker = RugChecker.RugChecker()
checker = PriceChecker.PriceChecker()
initial_investment = checker.fetch_price("So11111111111111111111111111111111111111112") * float(os.getenv("SOLANA_AMOUNT"))

fee_per_transaction = 0.4

is_processing = False
total_profit = 0.0

ADDRESS_REGEX = re.compile(r'\b[A-HJ-NP-Za-km-z1-9]{43,44}\b')

def extract_address(message_text):
    match = ADDRESS_REGEX.search(message_text)
    if match:
        return match.group(0)
    return None

def process_token(selected_token):
    global is_processing, total_profit
    try:
        processed_symbols = []
        total_time_minutes = 0

        print(f"Processing token: {selected_token}")

        initial_investment = checker.fetch_price("So11111111111111111111111111111111111111112") * float(os.getenv("SOLANA_AMOUNT"))

        initial_price = checker.fetch_price(selected_token)
        logger.sendMessageLog(f"{selected_token} received")

        if initial_price is None:
            print("Could not fetch the initial price.")
            return

        last_price = initial_price
        cumulative_percentage = 0.0
        unchanged_count = 0
        last_percentage_change = None

        while True:
            time.sleep(1)
            current_price = checker.fetch_price(selected_token)

            if current_price is None:
                print("Failed to fetch the current price. Skipping this iteration.")
                continue

            percentage_change_from_initial = ((current_price - initial_price) / initial_price) * 100
            percentage_change_from_last = ((current_price - last_price) / last_price) * 100

            print(f"Percentage change from initial: {percentage_change_from_initial:.2f}%")
            print(f"Percentage change from last price: {percentage_change_from_last:.2f}%")

            if last_percentage_change is not None and percentage_change_from_last == last_percentage_change:
                unchanged_count += 1
            else:
                unchanged_count = 0

            last_percentage_change = percentage_change_from_last

            if unchanged_count >= 7:
                logger.sendMessageLog("Unchanged for 7 seconds")
                return

            cumulative_percentage += percentage_change_from_last

            if percentage_change_from_last >= 1:
                logger.sendMessageLog("Buying token...")
                break

            if abs(percentage_change_from_initial) >= 60 or cumulative_percentage >= 60:
                logger.sendMessageLog("Significant price drop detected.")
                return

            last_price = current_price

        logger.sendMessageLog(f"{selected_token} swapped successfully")

        start_time = time.time()
        profit = checker.track_price_change(selected_token, initial_investment)
        total_profit += (profit - fee_per_transaction)  # Update total profit
        processed_symbols.append({
            'tokenSymbol': selected_token,
            'profit': profit - fee_per_transaction
        })
        end_time = time.time()
        elapsed_minutes = (end_time - start_time) / 60
        total_time_minutes += elapsed_minutes

        print(f"Profit for {selected_token}: {profit}")

        report_sender.sendReport(processed_symbols, total_time_minutes, initial_investment)
        report_sender.sendReport(f"Total profit on exit: {total_profit}")


    except Exception as e:
        print(f"Error processing token {selected_token}: {e}")
    finally:
        is_processing = False

@client.on(events.NewMessage(chats='signalsolanaby4am'))
async def handler(event):
    global is_processing
    message_text = event.message.message
    print(message_text)

    selected_token = extract_address(message_text)

    if selected_token:
        if not is_processing:
            is_processing = True
            print(f"New token detected: {selected_token}")
            process_token(selected_token)
        else:
            print("Currently processing a token. Ignoring this message.")

async def main():
    print("Listening for new messages...")
    logger.sendMessageLog("Listening for new messages...")
    await client.start()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
