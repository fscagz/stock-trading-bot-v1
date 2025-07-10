# atr_watchlist.py
 
import yfinance as yf
import pandas as pd
import time

def get_sp500_tickers():
 '''
 Fetches the list of S&P 500 ticker symbols from Wikipedia.
 Input: None
 Output: List of ticker strings formatted for Yahoo Finance (e.g., 'BRK-B' instead of 'BRK.B')
'''
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    tickers = table[0]["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]  # BRK.B → BRK-B

def compute_atr(ticker, period=14): 
 '''
 Calculates the 14-day Average True Range (ATR) for a given stock ticker using historical daily data.
 Input: 
   - ticker (str): Stock ticker symbol
   - period (int): Number of periods to use for ATR calculation (default is 14)
 Output: 
   - float: The computed ATR value, or None if data is insufficient or an error occurs
'''
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < period + 1:
            return None
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = df['TR'].rolling(window=period).mean().iloc[-1]
        return atr
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def get_top_atr_stocks(top_n, batch_size=50):
 '''
Processes all S&P 500 tickers in batches, computes their ATRs, and returns the top N stocks with the highest ATR values.
Input:
  - top_n (int): Number of top stocks to return based on ATR
  - batch_size (int): Number of tickers to process per batch (default is 50)
Output:
  - List of tuples: Each tuple contains (ticker, ATR), sorted by ATR in descending order
 '''
    tickers = get_sp500_tickers()
    all_results = []

    print(f"Scanning {len(tickers)} tickers in batches of {batch_size}...")

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"Processing batch {i // batch_size + 1}...")
        for ticker in batch:
            atr = compute_atr(ticker)
            if atr is not None:
                all_results.append((ticker, atr))
        time.sleep(1)  # Be polite to Yahoo's servers

    sorted_results = sorted(all_results, key=lambda x: x[1], reverse=True)
    print(f"\nTop {top_n} S&P 500 Stocks by ATR:")
    for ticker, atr in sorted_results[:top_n]:
        print(f"{ticker}: ATR = {atr:.2f}")

    return sorted_results[:top_n]

if __name__ == "__main__":
    get_top_atr_stocks()
