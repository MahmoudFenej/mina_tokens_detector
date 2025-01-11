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
    detected_token = "HREdVBmGvUvdgvoGeHwYpEQNJRb1oqmScwV5z1dHpump"
    
    buyerManager = BuyerManager.BuyerManager(detected_token)
    await buyerManager.perform_swap()

    time.sleep(20)

    sellManager = SellerManager.SellerManager(detected_token)
    await sellManager.perform_swap()

client.loop.run_until_complete(main())