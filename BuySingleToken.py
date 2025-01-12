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
import SellerManager


api_id = '26844985'
api_hash = 'db202faf086c8e0ad4f155b6e4c2eaf5'
report_sender = TelegramReport.TelegramReport()
logger = TelegramLogger.TelegramLogger()

session_string = '1BJWap1wBu3fJnP1xmcgIK2ZjnEvpTqhWeVtvBD4NU4H7UN7zRrC373q9qVR2Jr4P4Lzw10VStbuLTzApQGLMSzYexNRDAH2se_t7QK6EoTCJJMSv8-GKs0lZBWQGnADX6dO7i7TmbKd-Wejn-Jf3PoonsM8GWgDeCp91YUqE0k_xHG89-_VjZ0nr6kpvH91NjDu8N24BYuvZuPfLdq4O2f0mDTmbyvSACNPxF0ASvjVB02G7Q6Z9VZQKgiCNERa3iWEn9aFXsdI6vOV_LTDR4Hj44P0bIHKDVl_jFYTRM-Fh508hb8htrACocXaQ0HPc83jr5DPxR_AeRr_9iVKlm7BNP-W4Hns='

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    selected_token = "EkYEVGrEc6JrXFfcULE5QvTqpyjnX3Hk4VPjQGQMpump"
    processed_symbols = []
    buyerManager = BuyerManager.BuyerManager(selected_token)
    await buyerManager.perform_swap()
    
    checker = PriceChecker.PriceChecker()
    
    initial_investment = checker.fetch_price("So11111111111111111111111111111111111111112") * float(os.getenv("SOLANA_AMOUNT"))

    start_time = time.time()
    profit = await checker.track_price_change(selected_token, initial_investment)
    total_profit += (profit - 0.4)  
    processed_symbols.append({
        'tokenSymbol': selected_token,
        'profit': profit - 0.4
    })
    end_time = time.time()
    elapsed_minutes = (end_time - start_time) / 60
    total_time_minutes += elapsed_minutes

    print(f"Profit for {selected_token}: {profit}")



    

client.loop.run_until_complete(main())