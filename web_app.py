import os
import time
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import validate_order_params
from bot.logging_config import setup_logging
from bot.ai_analyst import AIAnalyst, CommandParser
from dotenv import load_dotenv

load_dotenv()
logger = setup_logging()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize Binance Client
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
futures_client = None
order_manager = None
ai_analyst = AIAnalyst()
command_parser = CommandParser()

# Global state for the "Automatic Bot"
bot_active = False
selected_symbol = "BTCUSDT"
trading_strategy = "RSI Scalper"
last_price = 0
price_history = [] # For RSI calculation

# Risk Settings
stop_loss_pct = 0.5
take_profit_pct = 1.0
position_size = 0.001

if api_key and api_secret:
    try:
        futures_client = BinanceFuturesClient(api_key, api_secret, testnet=True).get_futures_client()
        order_manager = OrderManager(futures_client)
        logger.info("Premium Bot: Binance Client initialized.")
    except Exception as e:
        logger.error(f"Premium Bot: Initialization failed: {e}")

# Background Task to simulate a "Real Bot" logic
def bot_loop():
    global last_price, bot_active
    while True:
        if futures_client and selected_symbol:
            try:
                ticker = futures_client.futures_symbol_ticker(symbol=selected_symbol.upper())
                price = float(ticker['price'])
                last_price = price
                price_history.append(price)
                if len(price_history) > 14:
                    price_history.pop(0)
                
                socketio.emit('price_update', {'price': price, 'symbol': selected_symbol})
                
                # Simple "Bot" Logic if active
                if bot_active and order_manager and len(price_history) >= 14:
                    # Calculate simple RSI
                    gains = []
                    losses = []
                    for i in range(1, len(price_history)):
                        diff = price_history[i] - price_history[i-1]
                        if diff > 0: gains.append(diff)
                        else: losses.append(abs(diff))
                    
                    avg_gain = sum(gains)/14 if gains else 0
                    avg_loss = sum(losses)/14 if losses else 0
                    
                    if avg_loss == 0: rsi = 100
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                    
                    # Trading Strategy: RSI Scalper
                    if rsi < 30: # Oversold -> BUY
                        logger.info(f"AutoBot: RSI {rsi:.2f} (Oversold). Placing BUY order.")
                        order_manager.place_order(selected_symbol, "BUY", "MARKET", position_size)
                        socketio.emit('bot_action', {'msg': f'AutoBot: RSI {rsi:.2f} - EXECUTED BUY'})
                    elif rsi > 70: # Overbought -> SELL
                        logger.info(f"AutoBot: RSI {rsi:.2f} (Overbought). Placing SELL order.")
                        order_manager.place_order(selected_symbol, "SELL", "MARKET", position_size)
                        socketio.emit('bot_action', {'msg': f'AutoBot: RSI {rsi:.2f} - EXECUTED SELL'})
                    
            except Exception as e:
                logger.error(f"Price Loop Error: {e}")
        time.sleep(5) # Throttle for testnet

@app.route('/api/market_stats')
def market_stats():
    try:
        ticker_24h = futures_client.futures_ticker(symbol=selected_symbol)
        return jsonify({
            'success': True,
            'high': ticker_24h['highPrice'],
            'low': ticker_24h['lowPrice'],
            'volume': ticker_24h['volume'],
            'priceChangePercent': ticker_24h['priceChangePercent']
        })
    except:
        return jsonify({'success': False}), 500

@app.route('/api/sentiment')
def sentiment():
    # Simulated sentiment based on price action
    if not price_history: return jsonify({'sentiment': 'Neutral', 'value': 50})
    change = (price_history[-1] - price_history[0]) / price_history[0] * 100
    if change > 0.5: return jsonify({'sentiment': 'Bullish', 'value': 75})
    if change < -0.5: return jsonify({'sentiment': 'Bearish', 'value': 25})
    return jsonify({'sentiment': 'Neutral', 'value': 50})

@app.route('/api/account')
def get_account():
    try:
        balance = futures_client.futures_account_balance()
        usdt_balance = next((item for item in balance if item["asset"] == "USDT"), None)
        return jsonify({
            'success': True,
            'balance': usdt_balance['balance'],
            'equity': usdt_balance['withdrawAvailable']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/positions')
def get_positions():
    try:
        positions = futures_client.futures_position_information()
        active_positions = [p for p in positions if float(p['positionAmt']) != 0]
        return jsonify({'success': True, 'positions': active_positions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update_risk', methods=['POST'])
def update_risk():
    global stop_loss_pct, take_profit_pct, position_size
    data = request.json
    stop_loss_pct = float(data.get('stop_loss', stop_loss_pct))
    take_profit_pct = float(data.get('take_profit', take_profit_pct))
    position_size = float(data.get('size', position_size))
    return jsonify({'success': True, 'msg': 'Risk settings updated'})

@app.route('/api/trades')
def get_trades():
    try:
        trades = futures_client.futures_account_trades(symbol=selected_symbol, limit=20)
        return jsonify({'success': True, 'trades': trades})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    try:
        trades = futures_client.futures_account_trades(symbol=selected_symbol, limit=50)
        if not trades:
            return jsonify({'success': True, 'win_rate': 0, 'total_pnl': 0, 'count': 0})
        
        total_pnl = sum(float(t['realizedPnl']) for t in trades)
        wins = len([t for t in trades if float(t['realizedPnl']) > 0])
        win_rate = (wins / len(trades)) * 100
        
        return jsonify({
            'success': True,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 4),
            'count': len(trades)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    symbol = request.args.get('symbol', selected_symbol).upper()
    interval = request.args.get('interval', '1m')
    try:
        klines = futures_client.futures_klines(symbol=symbol, interval=interval, limit=100)
        formatted_klines = []
        for k in klines:
            formatted_klines.append({
                'time': k[0] / 1000, # Convert to seconds
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4])
            })
        return jsonify({'success': True, 'data': formatted_klines})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['POST'])
def update_config():
    global selected_symbol, bot_active
    data = request.json
    selected_symbol = data.get('symbol', 'BTCUSDT').upper()
    bot_active = data.get('active', False)
    return jsonify({'success': True, 'bot_active': bot_active, 'symbol': selected_symbol})

@app.route('/api/place_order', methods=['POST'])
def place_order():
    if not order_manager:
        return jsonify({'success': False, 'error': 'Keys not configured'}), 400
    
    data = request.json
    response, error = order_manager.place_order(
        data.get('symbol'), 
        data.get('side'), 
        data.get('type'), 
        data.get('qty'), 
        data.get('price')
    )
    
    if error: return jsonify({'success': False, 'error': error}), 500
    return jsonify({'success': True, 'data': response})

@app.route('/api/ai_insight', methods=['POST'])
def ai_insight():
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    price = data.get('price', '0')
    insight = ai_analyst.get_market_insight(symbol, price)
    return jsonify({'success': True, 'insight': insight})

@app.route('/api/chat', methods=['POST'])
def chat():
    if not order_manager:
        return jsonify({'success': False, 'error': 'Binance keys not configured'}), 400
        
    data = request.json
    user_msg = data.get('message', '')
    
    # 1. Ask AI to parse the command
    command = command_parser.parse_message(user_msg, selected_symbol)
    
    if command['action'] == 'TRADE':
        # Execute the trade
        response, error = order_manager.place_order(
            command['symbol'], 
            command['side'], 
            command['type'], 
            command['qty'], 
            command['price']
        )
        
        if error:
            return jsonify({
                'success': False, 
                'message': f"I tried to execute that trade but Binance returned an error: {error}",
                'type': 'bot'
            })
            
        return jsonify({
            'success': True, 
            'message': f"🚀 Order Executed! {command['side']} {command['qty']} {command['symbol']} at {command['type']}. Order ID: {response.get('orderId')}",
            'type': 'bot'
        })
    
    elif command['action'] == 'ANALYZE':
        insight = ai_analyst.get_market_insight(command['symbol'], last_price)
        return jsonify({
            'success': True, 
            'message': insight,
            'type': 'bot'
        })
    
    else:
        # Default fallback if no command detected
        return jsonify({
            'success': True, 
            'message': "I'm not sure how to help with that. Try saying 'Buy 0.01 BTC' or 'What do you think about ETH?'",
            'type': 'bot'
        })

if __name__ == '__main__':
    # Start the background price thread
    threading.Thread(target=bot_loop, daemon=True).start()
    socketio.run(app, debug=True, port=5000)
