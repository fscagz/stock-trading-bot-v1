import yfinance as yf
import pandas as pd

def get_intraday_data(symbol: str, interval: str = "15m", period: str = "5d") -> pd.DataFrame:
    '''
    Gets intraday data from yfinance.
    symbol: ticker symbol for stock
    interval: bar interval (e.g., "1m", "5m", "15m", etc.)
    period: data range (e.g., "1d", "5d", etc.)

    Returns:
        pd.DataFrame containing OHLCV data with timestamps as index
    '''

    df = yf.download(
        tickers=symbol,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=False  # Explicitly set to avoid unexpected column formats
    )

    if df.empty:
        raise ValueError(f"No data returned for {symbol} with interval={interval} and period={period}")
    
    df.dropna(inplace=True)
    df.index.name = "Timestamp"

    # Handle multi-level columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip().capitalize() for col in df.columns.values]
    else:
        df.columns = [col.capitalize() for col in df.columns]

    return df

def get_5min_data(symbol: str, days_back: int = 5) -> pd.DataFrame:
    df = yf.download(
        tickers=symbol,
        period=f"{days_back}d",
        interval="5m",
        progress=False,
        auto_adjust=False
    )

    df = df[df.index.dayofweek < 5]
    df = df.between_time("09:30", "15:30")
    df.dropna(inplace=True)

    # Flatten and clean column names
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip().lower().replace(f"_{symbol.lower()}", "") for col in df.columns]
    else:
        df.columns = [col.lower().replace(f"_{symbol.lower()}", "") for col in df.columns]

    df.index.name = "timestamp"

    return df

'''
if __name__ == "__main__":
    spy_df = get_intraday_data("SPY", interval="15m", period="5d")
    print(spy_df.head())
'''
