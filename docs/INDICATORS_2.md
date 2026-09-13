# Indicators Deep Documentation

## Complete Indicator List with Gold & BTC Optimized Parameters

### 1. Moving Averages
- **EMA 21/50/200:** Short-medium-long trend. Price above EMAs = bullish bias. Pullback entries near EMA zone high probability.
  - XAUUSD: EMA 21/50 for short-medium, 50/200 for long bias
  - BTCUSD: EMA 20/50/200 with filter
- **SMA:** Simple, equal weight, smoothest trend.

### 2. RSI (Relative Strength Index)
- Measures momentum, not just overbought/oversold.
- RSI >50 bullish momentum, <50 bearish, divergence early warning exhaustion.
- XAUUSD: Works best with trend confirmation, not standalone.
- BTCUSD: RSI divergence followed by 10% correction to $64,555 observed. Use RSI slope for direction change.
- Settings: RSI 14 standard, RSI 60 for gold strategy with MA.

### 3. MACD - CORE SUPER PREDICTION
- Definition: MACD(n1,n2,n3) = EMA(n1)-EMA(n2), Signal = EMA(MACD, n3)
- Traditional (12,26,9) NOT optimal for gold. Appel suggested (8,17,9) buy, (12,25,9) sell.
- **Gold Optimized (MDPI 2025 Research):** n1 5-9 best, 17-20 worst. Performance depends on joint configuration.
- **BTC Optimized:** MACD consistently highest accuracy 73.21% GRU, 73.84% LSTM.
- **Zero-line vs Signal-line:** Histogram crossing zero = MACD line crossing zero = more significant momentum event than MACD crossing signal line.
- **Standardized MACD (MacNorm):** Normalized -1 to +1, enhanced for comparability across market conditions, mean reversion 25% return backtest.
- **Gold Tuned:** MACD 15-35-9 for XAUUSD scalping with EMA14, RSI14, Stoch, BB, VWAP filter.

### 4. Bollinger Bands
- Volatility + squeeze detection. TTM squeeze: BB inside Keltner for coil, expansion = release.
- Settings: 20/2.0 standard. Minimum volatility threshold for high volatility detection.

### 5. ATR (Average True Range)
- Dynamic SL, TP, avoid low volatility. Gold volatile ATR scaling essential.
- SL = 1.5*ATR, TP = 3*ATR. Instead of fixed pips, risk scales with market.

### 6. VWAP
- Intraday traders VWAP reclaims, institutional benchmark.

### 7. Stochastic, ADX, Keltner, Supertrend
- Stochastic RSI overbought/oversold
- ADX trend strength
- Keltner channel: EMA of price vs EMA of RSI for BTC futures
- Supertrend ATR-based adaptive trend filter tuned for gold volatility

### 8. On-Chain (BTC Only)
- 365-day MA $81,700 bull confirmation, 200-day MA $70K support
- Supply wall $77.1-80.2K where 539K BTC sold = heaviest resistance
- SOPR, Supply Weighted MA for cheap/expensive channel
- Funding rates, Open Interest, LSR 0.90-1.10 balanced
