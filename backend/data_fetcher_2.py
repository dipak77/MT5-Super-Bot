"""
Data Fetcher - Historical + Live
Generates sample CSVs and fetches live via MT5/CCXT
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataFetcher:
    def __init__(self):
        os.makedirs("historical_data", exist_ok=True)

    def generate_sample_csv(self, symbol, filename, days=400):
        """Generate realistic sample 15m data for backtesting"""
        base = 4320 if "XAU" in symbol else 77172
        periods = days * 24 * 4  # 15m
        dates = [datetime.now() - timedelta(minutes=15*i) for i in range(periods)][::-1]
        prices = []
        price = base
        np.random.seed(42 if "XAU" in symbol else 84)
        for i in range(periods):
            # Add trend + mean reversion + shocks
            drift = 0
            if i % 1000 == 0:
                drift = np.random.choice([-1,1]) * base * 0.02
            price += np.random.randn() * base * 0.0008 + drift * 0.001
            prices.append(price)
        
        df = pd.DataFrame({
            "Date": dates,
            "Open": [p + np.random.randn()*0.5 for p in prices],
            "High": [p + abs(np.random.randn()*2) for p in prices],
            "Low": [p - abs(np.random.randn()*2) for p in prices],
            "Close": prices,
            "Volume": [int(abs(np.random.randn()*500)+1000) for _ in prices]
        })
        df["High"] = df[["Open","Close","High"]].max(axis=1)
        df["Low"] = df[["Open","Close","Low"]].min(axis=1)
        df.to_csv(filename, index=False)
        print(f"Generated {filename} {len(df)} rows")
        return df

    def load_csv(self, filename):
        if os.path.exists(filename):
            return pd.read_csv(filename, parse_dates=["Date"])
        return pd.DataFrame()

if __name__ == "__main__":
    fetcher = DataFetcher()
    fetcher.generate_sample_csv("XAUUSD", "historical_data/XAUUSD_15m_2024_2026.csv", days=400)
    fetcher.generate_sample_csv("BTCUSD", "historical_data/BTCUSD_15m_2024_2026.csv", days=400)
