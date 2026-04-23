import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

load_dotenv()

class BinanceFuturesClient:
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET')
        self.testnet = testnet
        
        # Initialize client
        # For Futures Testnet, we set testnet=True in the Client constructor
        # and it will automatically use the testnet URLs if handled by python-binance
        # However, to be explicit as per requirements:
        self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)
        
        # Testnet base URL is handled internally by python-binance when testnet=True
        # but we can verify/set it if needed.
        if self.testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

    def get_futures_client(self):
        return self.client
