# signal_generator.py
'''
Generates trading signals based on price crossing above or below VWAP and 20-bar SMA.
Logic:
  - Entry Long (1): When price crosses above both VWAP and SMA from below
  - Exit Long (0): When price drops below either VWAP or SMA while in a long position
  - Entry Short (-1): When price crosses below both VWAP and SMA from above
  - Exit Short (0): When price rises above either VWAP or SMA while in a short position
Input:
  - df (pd.DataFrame): DataFrame with 'close', 'vwap', and 'sma_20' columns
  - verbose (bool): If True, prints signal events with timestamps
Output:
  - pd.Series: Series of trading signals (1 for long, -1 for short, 0 for exit/hold)
'''
import pandas as pd

def generate_signal(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    df = df.copy()

    for col in ["close", "vwap", "sma_20"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        
    df["signal"] = 0
    df["position"] = 0
    current_position = 0

    for i in range(1, len(df)): 
        close = df["close"].iloc[i]
        vwap = df["vwap"].iloc[i]
        sma = df["sma_20"].iloc[i]

        prev_close = df["close"].iloc[i - 1]
        prev_vwap = df["vwap"].iloc[i - 1]
        prev_sma = df["sma_20"].iloc[i - 1]

        timestamp = df.index[i]

        # === ENTRY LONG ===
        if (current_position == 0 
            and (prev_close <= prev_vwap or prev_close <= prev_sma)
            and close > vwap and close > sma):
            
            df.at[timestamp, "signal"] = 1
            current_position = 1
            if verbose:
                print(f"[{timestamp}] LONG ENTRY")

        # === EXIT LONG ===
        elif current_position == 1 and (close < vwap or close < sma):
            df.at[timestamp, "signal"] = 0
            current_position = 0
            if verbose:
                print(f"[{timestamp}] EXIT LONG")

        # === ENTRY SHORT ===
        elif (current_position == 0 
              and (prev_close >= prev_vwap or prev_close >= prev_sma)
              and close < vwap and close < sma):
            
            df.at[timestamp, "signal"] = -1
            current_position = -1
            if verbose:
                print(f"[{timestamp}] SHORT ENTRY")

        # === EXIT SHORT ===
        elif current_position == -1 and (close > vwap or close > sma):
            df.at[timestamp, "signal"] = 0
            current_position = 0
            if verbose:
                print(f"[{timestamp}] EXIT SHORT")

        # Set position column regardless
        df.at[timestamp, "position"] = current_position

    return df["signal"]


'''
# Old version of function, disregard
def generate_signal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in ["close", "vwap", "sma_20"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["signal"] = 0
    long_condition = (df["close"] > df["vwap"]) & (df["close"] > df["sma_20"])
    short_condition = (df["close"] < df["vwap"]) & (df["close"] < df["sma_20"])

    df.loc[long_condition, "signal"] = 1
    df.loc[short_condition, "signal"] = -1

    return df

'''
