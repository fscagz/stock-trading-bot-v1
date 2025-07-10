import os
import time
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderStatus

HEARTBEAT_FILE = "heartbeat.txt"

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

client = TradingClient(API_KEY, API_SECRET, paper=True)

def check_heartbeat():
    '''
 Checks the freshness of the heartbeat file to ensure the trading bot is still running.
 Input: None (reads from 'heartbeat.txt')
 Output: 
   - True if the heartbeat is recent (within 5 minutes)
   - False if the file is missing, stale, or improperly formatted
    '''
    if not os.path.exists(HEARTBEAT_FILE):
        print("[ALERT] No heartbeat file found!")
        return False
    with open(HEARTBEAT_FILE, "r") as f:
        last_heartbeat = f.read().strip()
    try:
        last_time = datetime.strptime(last_heartbeat, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("[ALERT] Heartbeat file has invalid format!")
        return False

    elapsed = (datetime.now() - last_time).total_seconds()
    if elapsed > 300:  # 5 minutes threshold
        print(f"[ALERT] Heartbeat stale! Last updated {elapsed:.1f} seconds ago.")
        return False
    print("[OK] Heartbeat is fresh.")
    return True

def check_account_status():
    '''
 Retrieves and prints current account status including cash, equity, buying power, and number of open positions.
 Input: None
 Output: Printed account summary to console
    '''
    account = client.get_account()
    positions = client.get_all_positions()
    print(
        f"Cash: ${float(account.cash):,.2f}, Equity: ${float(account.equity):,.2f}, "
        f"Buying Power: ${float(account.buying_power):,.2f}, Positions: {len(positions)}"
    )

def check_open_orders():
    '''
 Checks for any open orders in the Alpaca account and prints their details.
 Input: None
 Output: Printed list of open orders or confirmation that none exist
    '''
    all_orders = client.get_orders()
    open_orders = [order for order in all_orders if order.status == OrderStatus.OPEN]
    if open_orders:
        print(f"[INFO] Open orders count: {len(open_orders)}")
        for order in open_orders:
            print(
                f"Order ID: {order.id}, Symbol: {order.symbol}, Qty: {order.qty}, "
                f"Side: {order.side}, Submitted At: {order.submitted_at}"
            )
    else:
        print("[OK] No open orders.")

def main_loop():
    '''
 Continuously monitors the trading bot by checking heartbeat, account status, and open orders every 60 seconds.
 Input: None
 Output: Periodic console output with monitoring information and alerts
    '''
    while True:
        print(f"\n--- Monitoring check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        heartbeat_ok = check_heartbeat()
        check_account_status()
        check_open_orders()

        if not heartbeat_ok:
            print("[WARNING] Consider restarting your trading bot or investigating issues.")

        time.sleep(60)  # Wait 1 minute between checks

if __name__ == "__main__":
    main_loop()
