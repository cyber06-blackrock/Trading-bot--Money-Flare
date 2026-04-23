import logging
from binance.exceptions import BinanceAPIException, BinanceOrderException

logger = logging.getLogger("trading_bot")

class OrderManager:
    def __init__(self, client):
        self.client = client

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        try:
            symbol = symbol.upper()
            side = side.upper()
            order_type = order_type.upper()
            
            logger.info(f"Attempting to place {order_type} {side} order for {symbol} - Qty: {quantity}, Price: {price}")
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
            }
            
            if order_type == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'  # Good Till Cancelled
            elif order_type == 'STOP_LIMIT':
                params['price'] = price
                params['stopPrice'] = stop_price
                params['timeInForce'] = 'GTC'

            # Using futures_create_order for USDT-M Futures
            response = self.client.futures_create_order(**params)
            
            logger.info(f"Order placed successfully. Response: {response}")
            return response, None
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error: {e.message} (Code: {e.code})"
            logger.error(error_msg)
            return None, error_msg
        except BinanceOrderException as e:
            error_msg = f"Binance Order Error: {e.message}"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
