import time
import datetime as dt
import pytz
import math
import os
import csv
from alpaca.trading.client import TradingClient
from broker_alpaca import submit_market_order, get_open_positions
from data_loader_yf import get_5min_data, get_intraday_data
from indicators import calculate_vwap, calculate_intraday_sma
from signal_generator import generate_signal
from atr_watchlist import get_top_atr_stocks, compute_atr

# Configuration
RISK_PER_TRADE_PCT = 0.01  # Lower per trade due to smarter sizing
MAX_POSITIONS = 25
DATA_DAYS = 10
MARKET_START = dt.time(9, 30)
MARKET_END = dt.time(15, 30)
WATCHLIST_REFRESH_HOUR = 8
TRADE_START = dt.time(10, 0)
TRADE_END = dt.time(15, 15)
ET = pytz.timezone("US/Eastern")

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
client = TradingClient(API_KEY, API_SECRET, paper=True)

position_tracker = {}  # symbol -> {entry_price, direction}

LOG_FILE = "trade_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "symbol", "side", "qty", "price", "type", "ATR"])

def write_heartbeat():
    with open("heartbeat.txt", "w") as f:
        f.write(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def is_market_open():
    now = dt.datetime.now(ET).time()
    return MARKET_START <= now <= MARKET_END

def is_trade_time():
    now = dt.datetime.now(ET).time()
    return TRADE_START <= now <= TRADE_END

def refresh_watchlist():
    print("[INFO] Refreshing ATR watchlist...")
    top_atr_stocks = get_top_atr_stocks(top_n=MAX_POSITIONS)
    print(f"[INFO] Watchlist updated with top {len(top_atr_stocks)} ATR stocks.")
    return top_atr_stocks

def get_account_equity():
    account = client.get_account()
    return float(account.equity)

def log_trade(symbol, side, qty, price, trade_type, atr):
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([dt.datetime.now(ET), symbol, side, qty, price, trade_type, atr])

def main():
    watchlist = refresh_watchlist()
    last_refresh_date = dt.datetime.now(ET).date()

    while True:
        write_heartbeat()
        now_et = dt.datetime.now(ET)
        current_date = now_et.date()

        if current_date > last_refresh_date and now_et.time() >= dt.time(WATCHLIST_REFRESH_HOUR, 0):
            watchlist = refresh_watchlist()
            last_refresh_date = current_date

        if is_market_open():
            equity = get_account_equity()

            print(f"[INFO] Market open. Equity: ${equity:.2f}")

            open_positions = get_open_positions()
            held_symbols = list(open_positions.keys())
            watchlist_symbols = [s for s, _ in watchlist]
            full_symbols = set(watchlist_symbols) | set(held_symbols)
            symbol_to_atr = dict(watchlist)
            watchlist = [(s, symbol_to_atr.get(s) or compute_atr(s)) for s in full_symbols]

            for symbol, atr in watchlist:
                try:
                    if atr is None:
                        print(f"[WARN] Couldn't compute ATR for {symbol}, skipping.")
                        continue

                    df = get_5min_data(symbol, days_back=DATA_DAYS)
                    df["ATR"] = atr
                    df["vwap"] = calculate_vwap(df)
                    df["sma_20"] = calculate_intraday_sma(df, window=20)
                    df["signal"] = generate_signal(df)

                    latest = df.iloc[-1]
                    latest_signal = latest["signal"]
                    latest_close = latest["close"]
                    current_volume = latest["volume"]
                    avg_volume = df["volume"].rolling(20).mean().iloc[-1]
                    current_position = open_positions.get(symbol, 0.0)

                    # 1-hour SMA filter
                    hourly_df = get_intraday_data(symbol, interval="60m", period="5d")
                    sma_50 = hourly_df["Close"].rolling(window=50).mean().iloc[-1]

                    if math.isnan(sma_50):
                        continue

                    # Apply trend rule
                    is_uptrend = latest_close > sma_50
                    is_downtrend = latest_close < sma_50

                    # Stop-loss / Take-profit
                    if symbol in position_tracker:
                        entry_price = position_tracker[symbol]["entry_price"]
                        direction = position_tracker[symbol]["direction"]

                        if direction == 1:
                            if latest_close <= entry_price - 1.5 * atr:
                                submit_market_order(symbol, current_position, "sell")
                                log_trade(symbol, "sell", current_position, latest_close, "stop_loss", atr)
                                del position_tracker[symbol]
                                continue
                            elif latest_close >= entry_price + 2.5 * atr:
                                submit_market_order(symbol, current_position, "sell")
                                log_trade(symbol, "sell", current_position, latest_close, "take_profit", atr)
                                del position_tracker[symbol]
                                continue

                        elif direction == -1:
                            if latest_close >= entry_price + 1.5 * atr:
                                submit_market_order(symbol, abs(current_position), "buy")
                                log_trade(symbol, "buy", abs(current_position), latest_close, "stop_loss", atr)
                                del position_tracker[symbol]
                                continue
                            elif latest_close <= entry_price - 2.5 * atr:
                                submit_market_order(symbol, abs(current_position), "buy")
                                log_trade(symbol, "buy", abs(current_position), latest_close, "take_profit", atr)
                                del position_tracker[symbol]
                                continue

                    # Entry logic
                    if not is_trade_time():
                        continue
                    if current_volume < 1.5 * avg_volume:
                        continue

                    dollar_risk = equity * RISK_PER_TRADE_PCT
                    qty = dollar_risk / (1.5 * atr)
                    if latest_signal == 1 and is_uptrend:
                        if current_position > 0:
                            continue
                        submit_market_order(symbol, qty, "buy")
                        log_trade(symbol, "buy", qty, latest_close, "entry", atr)
                        position_tracker[symbol] = {"entry_price": latest_close, "direction": 1}

                    elif latest_signal == -1 and is_downtrend:
                        if current_position < 0:
                            continue
                        if qty < 1:
                            continue
                        qty = math.floor(qty)
                        submit_market_order(symbol, qty, "sell")
                        log_trade(symbol, "sell", qty, latest_close, "entry", atr)
                        position_tracker[symbol] = {"entry_price": latest_close, "direction": -1}

                    elif latest_signal == 0:
                        if current_position > 0:
                            submit_market_order(symbol, current_position, "sell")
                            log_trade(symbol, "sell", current_position, latest_close, "exit", atr)
                            position_tracker.pop(symbol, None)
                        elif current_position < 0:
                            submit_market_order(symbol, abs(current_position), "buy")
                            log_trade(symbol, "buy", abs(current_position), latest_close, "exit", atr)
                            position_tracker.pop(symbol, None)

                except Exception as e:
                    print(f"[ERROR] {symbol}: {e}")

            time.sleep(300)

        else:
            print("[INFO] Market is closed. Sleeping for 5 minutes...")
            time.sleep(300)

if __name__ == "__main__":
    main()