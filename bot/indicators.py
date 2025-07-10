# indicators.py

# Implements VWAP strategy using 20-bar simple moving average

import pandas as pd

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["tp_x_volume"] = df["typical_price"] * df["volume"]
    df["date"] = df.index.date

    df["cum_tp_vol"] = df.groupby("date")["tp_x_volume"].cumsum()
    df["cum_vol"] = df.groupby("date")["volume"].cumsum()

    vwap = df["cum_tp_vol"] / df["cum_vol"]
    vwap.name = "vwap"
    return vwap


def calculate_intraday_sma(df: pd.DataFrame, window) -> pd.Series:
    df = df.copy()
    df["Date"] = df.index.date
    sma = df.groupby("Date")["close"].rolling(window=window).mean()
    sma.index = sma.index.droplevel(0)
    return sma
