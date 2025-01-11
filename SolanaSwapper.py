from solders.keypair import Keypair
from solanatracker import SolanaTracker
import asyncio
import time

class SolanaSwapper:
    def __init__(self, private_key: str, rpc_url: str):
        self.keypair = Keypair.from_base58_string(private_key)
        self.rpc_url = rpc_url
        self.solana_tracker = SolanaTracker(self.keypair, rpc_url)

    async def swap(self, from_token: str, to_token: str, amount, slippage: float, priority_fee: float, priority_level:str):
        start_time = time.time()

        swap_response = await self.solana_tracker.get_swap_instructions(
            from_token,
            to_token,
            amount,
            slippage,
            str(self.keypair.pubkey()),
            priority_fee,
            priority_level,
        )
        

        custom_options = {
            "send_options": {"skip_preflight": True, "max_retries": 5},
            "confirmation_retries": 50,
            "confirmation_retry_timeout": 1000,
            "last_valid_block_height_buffer": 200,
            "commitment": "processed",
            "resend_interval": 1500,
            "confirmation_check_interval": 100,
            "skip_confirmation_check": False,
        }

        try:
            # Perform the swap
            send_time = time.time()
            txid = await self.solana_tracker.perform_swap(swap_response, options=custom_options)
            end_time = time.time()
            elapsed_time = end_time - start_time

            print("Transaction ID:", txid)
            print("Transaction URL:", f"https://solscan.io/tx/{txid}")
            print(f"Swap completed in {elapsed_time:.2f} seconds")
            print(f"Transaction finished in {end_time - send_time:.2f} seconds")
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Swap failed:", str(e))
            print(f"Time elapsed before failure: {elapsed_time:.2f} seconds")

# Example usage
if __name__ == "__main__":
    private_key = ""
    rpc_url = "https://rpc.solanatracker.io/public?advancedTx=true"

    swapper = SolanaSwapper(private_key, rpc_url)

    # ape = "HREdVBmGvUvdgvoGeHwYpEQNJRb1oqmScwV5z1dHpump"

    # sol = "So11111111111111111111111111111111111111112" 
    from_token = "HREdVBmGvUvdgvoGeHwYpEQNJRb1oqmScwV5z1dHpump" 
    # to_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  
    to_token = "So11111111111111111111111111111111111111112"  

    amount = "auto"  
    slippage = 30 
    priority_fee = 0.0005 

    asyncio.run(swapper.swap(from_token, to_token, amount, slippage, priority_fee))
