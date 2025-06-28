# data_loader.py

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
from datetime import datetime, timedelta
import os

# Load credentials from environment variables or fallback
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_SECRET_KEY")

# Initialize Alpaca data client
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

def get_15min_data(symbol: str, days_back: int = 10) -> pd.DataFrame:
    '''
    Downloads 15-minute historical bars for a given symbol using alpaca-py
    '''

    end_time = datetime.now()
    start_time = end_time - timedelta(days=days_back)

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=start_time,
        end=end_time,
    )

    bars = client.get_stock_bars(request_params).df

    # Filter for the specific symbol if multiple returned
    bars = bars[bars.index.get_level_values("symbol") == symbol]

    # Resample to 15-minute intervals
    bars = bars.resample("15T").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    }).dropna()

    bars.index.name = "timestamp"

    return bars

# For manual testing
if __name__ == "__main__":
    df = get_15min_data("SPY", days_back=6)
    print(df.head())
