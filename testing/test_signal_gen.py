# test_signal_generator.py

import pandas as pd
from signal_generator import generate_signal

# Create sample intraday DataFrame
data = {
    "close":   [100, 102, 101, 98, 97, 99, 100],
    "vwap":    [101, 101, 101, 100, 99, 100, 101],
    "sma_20":  [99, 99, 99, 99, 99, 99, 99]
}
index = pd.date_range("2025-06-02 09:30", periods=7, freq="5min")
df = pd.DataFrame(data, index=index)

# Run signal generator
df_with_signals = generate_signal(df, verbose=True)

# Output result
print(df_with_signals[["close", "vwap", "sma_20", "signal"]])
