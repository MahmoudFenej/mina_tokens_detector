import asyncio
import SolanaSwapper
from dotenv import load_dotenv
import os

load_dotenv()

class BuyerManager:
    def __init__(self, to_token):
        self.to_token = to_token
        self.private_key = "2KgV9AdQPxNC7aFNm1Us1CjZUBg8zP8UgPGTbnCwFxxzECQeZG1Z4Pt9BPj81kC6niijJT2TePVVf7w3FzbMh4MK"
        self.rpc_url = "https://rpc.solanatracker.io/public?advancedTx=true"

        self.amount = float(os.getenv("SOLANA_AMOUNT")) 
        self.slippage = float(os.getenv("SLIPPAGE"))
        self.priority_fee = os.getenv("PRIORITY_FEE")
        self.priority_level = os.getenv("PRIORITY_LEVEL")
        
        self.swapper = SolanaSwapper.SolanaSwapper(self.private_key, self.rpc_url)

    async def perform_swap(self):
        from_token = "So11111111111111111111111111111111111111112" 
        try:
            await self.swapper.swap(from_token, self.to_token, self.amount, self.slippage, self.priority_fee, self.priority_level)
        except Exception as e:
            print(f"Error occurred during swap: {e}")
        finally:
            print("Swap attempt completed.")
