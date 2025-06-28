# atr_watchlist.py
 
import yfinance as yf
import pandas as pd
import time

# Get list of S&P 500 tickers
def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    tickers = table[0]["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]  # BRK.B → BRK-B

# Compute 14-period ATR for a given ticker
def compute_atr(ticker, period=14):
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

# Main: batch process all tickers
def get_top_atr_stocks(top_n, batch_size=50):
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
