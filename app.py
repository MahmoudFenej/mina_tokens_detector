import re
import time
from telethon import TelegramClient, events
import TelegramReport
import PriceChecker
from dotenv import load_dotenv
import os
import TelegramLogger
from datetime import datetime
from telethon.sessions import StringSession
import BuyerManager

load_dotenv()

api_id = '26844985'
api_hash = 'db202faf086c8e0ad4f155b6e4c2eaf5'
report_sender = TelegramReport.TelegramReport()
logger = TelegramLogger.TelegramLogger()

session_string = '1BJWap1wBu3fJnP1xmcgIK2ZjnEvpTqhWeVtvBD4NU4H7UN7zRrC373q9qVR2Jr4P4Lzw10VStbuLTzApQGLMSzYexNRDAH2se_t7QK6EoTCJJMSv8-GKs0lZBWQGnADX6dO7i7TmbKd-Wejn-Jf3PoonsM8GWgDeCp91YUqE0k_xHG89-_VjZ0nr6kpvH91NjDu8N24BYuvZuPfLdq4O2f0mDTmbyvSACNPxF0ASvjVB02G7Q6Z9VZQKgiCNERa3iWEn9aFXsdI6vOV_LTDR4Hj44P0bIHKDVl_jFYTRM-Fh508hb8htrACocXaQ0HPc83jr5DPxR_AeRr_9iVKlm7BNP-W4Hns='

client = TelegramClient(StringSession(session_string), api_id, api_hash)
checker = PriceChecker.PriceChecker()

print(os.getenv("SOLANA_AMOUNT"))


initial_investment =  float(os.getenv("SOLANA_AMOUNT"))

fee_per_transaction = 0.4

total_profit = 0.0

ADDRESS_REGEX = re.compile(r'\b[A-HJ-NP-Za-km-z1-9]{43,44}\b')

def extract_address(message_text):
    match = ADDRESS_REGEX.search(message_text)
    if match:
        return match.group(0)
    return None

async def process_token(selected_token):
    global total_profit
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

        consistent_increase = False
        for i in range(2):
            if i == 1:
                time.sleep(2)
                current_price = checker.fetch_price(selected_token)
                price_increase_percentage = ((current_price - initial_price) / initial_price) * 100
                logger.sendMessageLog(f"Initial Price for {selected_token}: {initial_price}")
                if price_increase_percentage >= 0.5:
                    initial_price = current_price
                    consistent_increase = True
                else:
                    consistent_increase = False
                    logger.sendMessageLog(f"Price did not increase consistently for {selected_token}. Skipping...")

        if not consistent_increase:
            return

        logger.sendMessageLog(f"{selected_token} swapped successfully")
        # buyerManager = BuyerManager.BuyerManager(selected_token)
        # await buyerManager.perform_swap()

        start_time = time.time()
        profit = await checker.track_price_change(selected_token, initial_investment)
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


    except Exception as e:
        print(f"Error processing token {selected_token}: {e}")

@client.on(events.NewMessage(chats='PumpFunPlays'))
async def handler(event):
    global is_processing
    message_text = event.message.message
    message_time = event.message.date 
    current_time = datetime.now()
    time_diff = current_time.timestamp() - message_time.timestamp()
    
    logger.sendMessageLog(f"New Message Received ${message_time}")

    if time_diff <= 30:
        selected_token = extract_address(message_text)
        if selected_token:
            print(f"New token detected: {selected_token}")
            await process_token(selected_token)
    else:
        logger.sendMessageLog(f"Message Dropped time diff {time_diff}")


async def main():
    logger.sendMessageLog("Listening for new messages...")
    await client.start()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
