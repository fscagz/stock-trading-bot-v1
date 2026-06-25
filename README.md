# Note

This repo is no longer being used. Please see v4.1 instead: https://github.com/fscagz/stock-trading-bot-v4.1

# Python Stock Trading Bot

A Python-based stock trading bot that integrates with the **Alpaca API** for live trading and uses **Yahoo Finance** for historical data. This modular system supports backtesting, live monitoring, and technical indicator-based signal generation. It works by calculating a stock's volume-weighted average price (VWAP) and trading when a significant deviation is detected.

Note: This is the first iteration and is still a work in progress. Currently working on improving trade logic and new trading strategies.

---

## 🚀 Features

- 📈 **Alpaca API Integration** – Place real-time trades via Alpaca brokerage.
- 📊 **Backtesting Engine** – Test strategies on historical data.
- 🔍 **Technical Indicators** – Includes ATR, Moving Averages, and more.
- 🧠 **Signal Generator** – Custom trading signals based on market conditions.
- 🕒 **Heartbeat Monitor** – Tracks the bot's liveness.
- 📡 **Live Watchlist Monitoring** – Track stocks using ATR-based volatility.

---

## 📁 Project Structure
```bash

stock-trading-bot-v1/
│
├── bot/                       # Core trading bot package
│   ├── main.py               # Main entry point
│   ├── broker_alpaca.py      # Alpaca API integration
│   ├── data_loader_yf.py     # Yahoo Finance data loading
│   ├── indicators.py         # Technical indicators
│   ├── signal_generator.py   # Signal generation logic
│   ├── atr_watchlist.py      # Watchlist based on ATR
│   ├── backtester.py         # Backtesting engine
│   ├── monitor.py            # Monitors performance and bot status
│   └── heartbeat.txt         # Keeps bot liveness signal
│
├── tests/                    # Unit and integration tests
│   ├── __init__.py
│   ├── test_alpaca_data.py
│   ├── test_backtester.py
│   ├── test_broker.py
│   ├── test_indicators.py
│   ├── test_portfolio.py
│   ├── test_signal_gen.py
│   └── test_yfinance_data.py
│
├── tests/                    # Files currently unused but included for reference
│   ├── data_loader.py        # Data loading using Alpaca API (requires paid account)
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
└── .gitignore                # Ignore Python caches, credentials, etc.

```
---

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/fscagz/python-trading-bot.git
cd python-trading-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```
## 🔑 Configuration

Set your Alpaca API keys using environment variables for better security.
Edit the stock symbols and parameters in main.py or relevant strategy files.

## ▶️ Running the Bot
```
python main.py
```
The bot will use signal_generator.py to create trade signals.
Trades are executed via broker_alpaca.py.
heartbeat.txt is updated regularly to indicate that the bot is alive.

## 🛠️ Requirements

Python 3.8+
alpaca-trade-api
yfinance
pandas
numpy
ta (Technical Analysis Library)

## 📌 Disclaimer!

This project is for educational purposes only. Trading involves risk, and past performance is not indicative of future results. Use at your own risk.
