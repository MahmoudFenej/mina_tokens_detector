import BuyerManager
import PriceChecker
import SellerManager
import time


if __name__ == "__main__":
    
    detected_token = "HBpekG4Ybxf57Kw17tsfcuB1bA5omaSZZViL3rzapump"
    
    checker = PriceChecker.PriceChecker()

    buyerManager = BuyerManager.BuyerManager(detected_token)
    buyerManager.perform_swap()

    # time.sleep(20)

    # sellManager = SellerManager.SellerManager(detected_token)
    # sellManager.perform_swap()
