from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

api_id = '26844985'  # Get from https://my.telegram.org/auth
api_hash = 'db202faf086c8e0ad4f155b6e4c2eaf5'  # Get from https://my.telegram.org/auth

# Create a new client with StringSession
with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Session string:", client.session.save())  # Print the session string
