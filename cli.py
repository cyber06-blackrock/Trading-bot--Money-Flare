import click
import os
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import validate_order_params
from bot.logging_config import setup_logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Setup logger
logger = setup_logging()

@click.group()
def cli():
    """Simplified Trading Bot for Binance Futures Testnet"""
    pass

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL'], case_sensitive=False), help='BUY or SELL')
@click.option('--type', 'order_type', required=True, type=click.Choice(['MARKET', 'LIMIT', 'STOP_LIMIT'], case_sensitive=False), help='Order type')
@click.option('--qty', required=True, type=float, help='Quantity to trade')
@click.option('--price', type=float, help='Price (required for LIMIT and STOP_LIMIT)')
@click.option('--stop-price', type=float, help='Stop Price (required for STOP_LIMIT)')
def place(symbol, side, order_type, qty, price, stop_price):
    """Place a new order on Binance Futures Testnet"""
    
    # 1. Validate inputs
    errors = validate_order_params(symbol, side, order_type, qty, price)
    if order_type.upper() == 'STOP_LIMIT' and stop_price is None:
        errors.append("Stop price is required for STOP_LIMIT orders.")
        
    if errors:
        for err in errors:
            click.echo(f"{Fore.RED}Error: {err}")
        return

    # 2. Initialize Binance Client
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        click.echo(f"{Fore.RED}Error: API Credentials missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file.")
        return

    try:
        futures_client = BinanceFuturesClient(api_key, api_secret, testnet=True).get_futures_client()
        order_manager = OrderManager(futures_client)
        
        # 3. Order Summary
        click.echo(f"\n{Fore.CYAN}--- Order Request Summary ---")
        click.echo(f"Symbol: {symbol.upper()}")
        click.echo(f"Side: {side.upper()}")
        click.echo(f"Type: {order_type.upper()}")
        click.echo(f"Quantity: {qty}")
        if price: click.echo(f"Price: {price}")
        if stop_price: click.echo(f"Stop Price: {stop_price}")
        click.echo(f"{Fore.CYAN}-----------------------------\n")

        # 4. Place Order
        response, error = order_manager.place_order(symbol, side, order_type, qty, price, stop_price)
        
        if error:
            click.echo(f"{Fore.RED}FAILED: {error}")
        else:
            click.echo(f"{Fore.GREEN}SUCCESS: Order placed successfully!")
            click.echo(f"{Fore.YELLOW}--- Order Response Details ---")
            click.echo(f"OrderID: {response.get('orderId')}")
            click.echo(f"Status: {response.get('status')}")
            click.echo(f"Executed Qty: {response.get('executedQty')}")
            click.echo(f"Avg Price: {response.get('avgPrice', 'N/A')}")
            click.echo(f"{Fore.YELLOW}------------------------------")

    except Exception as e:
        click.echo(f"{Fore.RED}An unexpected error occurred: {str(e)}")
        logger.error(f"CLI Exception: {str(e)}")

if __name__ == '__main__':
    cli()
