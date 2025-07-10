# broker_alpaca.py

import os
# from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# load_dotenv()
'''
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")
'''
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

def get_account_info():
    account = trading_client.get_account()
    return {
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "portfolio_value": float(account.portfolio_value),
        "status": account.status
    }

def get_open_positions():
    positions = trading_client.get_all_positions()
    return {p.symbol: float(p.qty) for p in positions}

def submit_market_order(symbol, qty, side = "buy"):
    order = MarketOrderRequest(
        symbol = symbol,
        qty = qty,
        side = OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force = TimeInForce.DAY
    )
    result = trading_client.submit_order(order)
    return result.id
