import yfinance as yf
import pandas as pd

def get_intraday_data(symbol: str, interval: str = "15m", period: str = "5d") -> pd.DataFrame:
    '''
 Fetches intraday OHLCV data for a given stock symbol using yfinance.
 Input:
   - symbol (str): Ticker symbol of the stock
   - interval (str): Time interval between data points (e.g., "1m", "5m", "15m")
   - period (str): Time span of data to retrieve (e.g., "1d", "5d")
 Output:
   - pd.DataFrame: DataFrame containing OHLCV data with timestamps as index
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
    '''
 Retrieves 5-minute interval intraday data for the past N weekdays, filtered to regular market hours.
 Input:
   - symbol (str): Ticker symbol of the stock
   - days_back (int): Number of past days to retrieve (default is 5)
 Output:
   - pd.DataFrame: Cleaned DataFrame with 5-minute OHLCV data during market hours (09:30–15:30)
    '''

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
