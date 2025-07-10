# backtester.py

'''
Simulates trades based on signal column
Assumes trade is entered on the same bar as signal is generated (at close)
'''
import pandas as pd

def backtest_signals(df: pd.DataFrame):
    '''
  Backtests trading signals by simulating long and short trades based on the 'signal' column.
  Input:
    - df (pd.DataFrame): DataFrame with a datetime index and at least two columns:
        'signal' (1 for long entry, -1 for short entry, 0 for exit)
        'close' (price at which trades are entered/exited)
  Output:
    - df (pd.DataFrame): Modified DataFrame with 'trade_pnl' and 'cumulative_pnl' columns
    - trades (list of dicts): List of executed trades with entry/exit details and PnL
    '''
    df = df.copy()
    df["trade_pnl"] = 0.0
    df["cumulative_pnl"] = 0.0

    trades = []
    position = 0
    entry_price = 0.0
    entry_time = None
    direction = None
    cumulative_pnl = 0.0

    for i in range(len(df)):
        row = df.iloc[i]
        timestamp = df.index[i]
        signal = row["signal"]
        price = row["close"]

        if signal == 1 and position == 0:
            # Enter long
            position = 1
            entry_price = price
            entry_time = timestamp
            direction = "long"
            print(f"[{timestamp}] LONG ENTRY at {price}")

        elif signal == -1 and position == 0:
            # Enter short
            position = -1
            entry_price = price
            entry_time = timestamp
            direction = "short"
            print(f"[{timestamp}] SHORT ENTRY at {price}")

        elif signal == 0 and position != 0:
            # Exit trade
            exit_price = price
            exit_time = timestamp

            if position == 1:
                pnl = exit_price - entry_price
            else:
                pnl = entry_price - exit_price

            holding_period = (df.index.get_loc(exit_time) - df.index.get_loc(entry_time))

            trades.append({
                "entry_time": entry_time,
                "exit_time": exit_time,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "direction": direction,
                "pnl": pnl,
                "holding_period": holding_period
            })

            df.at[timestamp, "trade_pnl"] = pnl
            cumulative_pnl += pnl
            df.at[timestamp, "cumulative_pnl"] = cumulative_pnl

            print(f"[{timestamp}] EXIT {direction.upper()} at {price} | PnL: {pnl}")

            # Reset
            position = 0
            entry_price = 0.0
            entry_time = None
            direction = None

        else:
            # No trade
            df.at[timestamp, "cumulative_pnl"] = cumulative_pnl

    return df, trades

