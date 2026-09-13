# Architecture - XAU-GOD v1 / BTC-GOD v1 Production

## System Architecture Diagram

```
[MT5 Terminal - Demo/Real] 
    ↓ (MT5 Python API / Mock)
[MT5Trader Connector]
    ↓ OHLCV
[Data Fetcher + Historical CSV]
    ↓
[Feature Engineering]
  - Candle Depth (body ratio, wick)
  - SR Zones (pivot detection)
  - Indicators (EMA, RSI, MACD, BB, ATR, VWAP)
  - On-Chain (BTC: 365-day MA, supply wall)
    ↓
[Regime Detection]
  - Volatility (ATR)
  - Trend (ADX, EMA alignment)
  - LSR (Long/Short ratio 0.90-1.10 balanced)
    ↓
[ML Prediction - Optional]
  - Attention-LSTM 73.84% accuracy with MACD
  - Standardized MACD mean reversion 25% backtest
    ↓
[Super Algo Signal Generation]
  - MACD WITH LE/SE super prediction
  - Top/Bottom matching last high/low
  - Pattern matching
  - Self prediction score 0-100
    ↓
[Risk Manager]
  - 0.5% risk per trade
  - ATR SL 1.5x, TP 3x
  - Daily loss limit 3%
  - Real trade confirmation
    ↓
[Execution]
  - MT5 order_send
  - Position monitor
    ↓
[Alert Manager]
  - WebSocket broadcast every 5s
  - Telegram bot
  - Browser notification
  - Log file
    ↓
[Frontend Dashboard]
  - Multi-timeframe viewer 2x2 grid
  - Realtime alerts
  - Positions monitor
  - Equity curve
```

## Data Flow - Depth Analysis

1. **Candle Depth:**
   - Body ratio = |Close-Open| / (High-Low)
   - >70% strong momentum, <30% doji indecision
   - Wick imbalance = Upper/Lower, long upper = resistance
   - Volume-price: high vol + small body at support = accumulation

2. **SR Detection:**
   - Pivot highs/lows with swing strength left=right bars
   - Zone states: Fresh (green support, red resistance), Broken (stops extending, marker at break)
   - Order Block & Breaker: close beyond zone flips polarity, former support becomes resistance
   - Confluence scoring: pivot + order block overlap within ATR distance

3. **Top/Bottom Prediction:**
   - Last Top = Highest high last 50 periods
   - Last Bottom = Lowest low last 50 periods
   - Distance in ATR: if <0.5 ATR near level
   - RSI divergence: price higher high + RSI lower high = double top risk
   - Rejection candle: wick >50% range = polarity flip confirmation

## Tech Stack

- Backend: FastAPI, Uvicorn, Pandas, Numpy, MetaTrader5 (Windows), python-telegram-bot
- Frontend: HTML5 Canvas (no external chart lib for performance), Tailwind CSS, Vanilla JS (standalone) + React optional
- Data: CCXT for Binance, MT5 history, Kaggle XAUUSD 2004-2024, Yahoo Finance BTC-USD
- ML: TensorFlow/Keras, pytorch-btc ONNX, CorrWeighted-LSTM
- Deployment: Windows for MT5, Oracle Free VPS, Docker optional

## Production Considerations

- MT5 only runs on Windows - backend runs mock mode on Linux/Mac for dev
- WebSocket reconnection logic
- Risk manager hard stops
- Telegram rate limiting
- Log rotation
- .env separation demo vs real
