# MoneyFlare Pro | Advanced AI Trading Terminal

A professional-grade, full-stack automated crypto trading terminal with real-time market data visualization, AI-powered execution, and automated scalping engines.

## Features
- **Real-time Visualization**: Integrated TradingView charts for deep market analysis.
- **AI Analyst**: Advanced AI-powered command center for natural language order execution and market insights.
- **Order Types**: Support for `MARKET`, `LIMIT`, and `STOP_LIMIT` orders on Binance Futures Testnet.
- **Automated Scalping**: Built-in RSI-based scalping engine for hands-free trading.
- **Analytics Dashboard**: Track trade history, win-rates, and real-time portfolio metrics.
- **Logging**: Detailed logs of all API requests and responses.

## Project Structure
```
trading_bot/
  bot/
    ai_analyst.py    # AI processing logic
    client.py        # Binance client wrapper
    orders.py        # Order placement logic
    validators.py    # Input validation
    logging_config.py# Logger setup
  templates/         # Web dashboard UI
  web_app.py         # Flask web application
  cli.py             # CLI entry point
  .env               # API credentials
  requirements.txt   # Dependencies
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Binance Futures Testnet Account
- OpenAI API Key (for AI features)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file with your credentials:
```env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
OPENAI_API_KEY=your_openai_key
```

### 4. Running the App
Start the web dashboard:
```bash
python web_app.py
```
Or use the CLI:
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

## Disclaimer
This software is for educational purposes only. Use at your own risk.
