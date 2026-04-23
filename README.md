# Simplified Trading Bot (Binance Futures Testnet)

A robust Python application for placing orders on the Binance Futures Testnet (USDT-M) with structured logging, input validation, and a clean CLI interface.

## Features
- **Order Types**: Support for `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
- **Side**: Support for both `BUY` and `SELL` operations.
- **Validation**: Robust input validation for symbols, quantities, and prices.
- **Logging**: Detailed logs of all API requests, responses, and errors saved to the `logs/` directory.
- **UX**: Enhanced CLI experience with colored output and clear summaries.

## Project Structure
```
trading_bot/
  bot/
    __init__.py
    client.py        # Binance client wrapper
    orders.py        # Order placement logic
    validators.py    # Input validation logic
    logging_config.py# Logger setup
  cli.py             # CLI entry point
  .env               # API credentials (not included in repo)
  requirements.txt   # Dependencies
  README.md          # Documentation
```

## Setup Instructions

### 1. Prerequisites
- Python 3.7+
- Binance Futures Testnet Account (Register at [testnet.binancefuture.com](https://testnet.binancefuture.com))
- API Key and Secret from the Testnet dashboard.

### 2. Installation
Clone the repository (or extract the zip) and navigate to the project folder:

```bash
cd trading_bot
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration
Rename `.env.example` to `.env` and add your Testnet API credentials:
```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

## Usage Examples

The bot uses a command-line interface. Use the `place` command to execute trades.

### Place a MARKET Order
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### Place a LIMIT Order
```bash
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 65000
```

### Place a STOP_LIMIT Order (Bonus Feature)
```bash
python cli.py place --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 --price 70000 --stop-price 69500
```

## Logging
All activities are logged in the `logs/` directory. Each session generates a log file named `trading_bot_YYYYMMDD.log`. These logs include:
- API Request details
- Full JSON responses from Binance
- Error messages and stack traces for debugging

## Assumptions
- The bot is strictly configured for the **USDT-M Futures Testnet**.
- Users have sufficient margin balance in their testnet account.
- Symbols must follow the Binance format (e.g., `BTCUSDT`, `ETHUSDT`).
- Quantity must meet the minimum lot size requirements for the specific symbol on Binance.
