# portfolio.py
'''
Computes portfolio stats
'''

import pandas as pd
import numpy as np

def analyze_trades(df: pd.DataFrame, verbose: bool = False) -> dict:
    trades = []
    entry_price = None
    entry_time = None
    direction = None

    equity_curve = []
    equity = 0

    for i in range(len(df)):
        row = df.iloc[i]
        signal = row.get("signal", 0)
        price = row["close"]
        time = row.name

        if signal == 1 or signal == -1:
            entry_price = price
            entry_time = time
            direction = signal
        elif signal == 0 and entry_price is not None:
            pnl = (price - entry_price) * direction
            holding_period = (time - entry_time).seconds / 60  # in minutes

            trades.append({
                "entry_time": entry_time,
                "exit_time": time,
                "entry_price": entry_price,
                "exit_price": price,
                "direction": direction,
                "pnl": pnl,
                "holding_period": holding_period
            })

            equity += pnl
            equity_curve.append(equity)

            if verbose:
                print(f"TRADE: {entry_time} -> {time} | Dir: {direction} | Entry: {entry_price} | Exit: {price} | PnL: {pnl}")

            entry_price = None
            entry_time = None
            direction = None

    if not trades:
        return {}

    trade_df = pd.DataFrame(trades)
    total_pnl = trade_df["pnl"].sum()
    num_trades = len(trade_df)
    wins = trade_df[trade_df["pnl"] > 0]
    losses = trade_df[trade_df["pnl"] < 0]
    win_rate = len(wins) / num_trades if num_trades else 0
    avg_pnl = trade_df["pnl"].mean()
    std_pnl = trade_df["pnl"].std(ddof=0) if num_trades > 1 else 0
    avg_holding_period = trade_df["holding_period"].mean()
    profit_factor = wins["pnl"].sum() / abs(losses["pnl"].sum()) if not losses.empty else float("inf")

    # Sharpe ratio (assumes 0 risk-free rate and 1 trade = 1 period)
    returns = df["trade_pnl"]
    mean_return = returns.mean()
    std_return = returns.std(ddof=1)
    sharpe_ratio = mean_return / std_return if std_return != 0 else 0.0


    # Max Drawdown
    cum_pnl = df['cumulative_pnl']
    running_max = cum_pnl.cummax()
    drawdowns = running_max - cum_pnl
    max_drawdown = drawdowns.max()

    return {
        "total_pnl": round(total_pnl, 2),
        "num_trades": num_trades,
        "win_rate": round(win_rate, 2),
        "avg_pnl_per_trade": round(avg_pnl, 2),
        "std_pnl": round(std_pnl, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "avg_holding_period_min": round(avg_holding_period, 2),
        "profit_factor": round(profit_factor, 2)
    }
