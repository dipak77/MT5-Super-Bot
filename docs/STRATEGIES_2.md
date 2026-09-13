# Strategies Documentation

## Indicators wise Strategies Table

| Indicator | Strategies Using It |
|-----------|---------------------|
| EMA 21/50/200 | Trend pullback, Golden Cross, Dynamic SR, Breakout confirmation |
| RSI 14/60 | RSI divergence, RSI + MA, RSI hook, Overbought/Oversold reversal, Slope change |
| MACD 5-9/26-35/9 | Zero-line cross, Signal cross, Volume Oscillator filter, BB cross, Standardized MacNorm mean reversion (25% return), MACD + Fear & Greed DCA, MACD + RSI confirmation |
| Bollinger Bands | Squeeze breakout, BB + RSI, Volatility threshold, Price outside BB + RSI + MACD entry |
| ATR | ATR stop loss, ATR TP scaling, Supertrend, Trailing stops |
| VWAP | VWAP reclaim intraday, VWAP + EMA filter |
| On-Chain 365d MA | Bull market confirmation close above $81,700 (BTC) |
| Funding/LSR | Sentiment, deleveraging detection |

## Strategies wise Indicators Table

| Strategy | Required Indicators & Logic |
|----------|----------------------------|
| **Trend Pullback (Best for XAUUSD)** | EMA21>EMA50, price near EMA zone, RSI>50, bullish candle confirmation, ATR SL, target previous high/resistance. Removes emotion with rules. |
| **Breakout** | Donchian, Volume expansion, MACD above zero, ATR. High liquidity reduces noise, respects key levels. |
| **Mean Reversion** | Standardized MACD MacNorm -1 to +1, Trigger WMA, Bollinger Bands, RSI. Assumes prices revert to long-term average. Identifies excessive deviations. |
| **DCA Enhanced (BTC)** | MACD + Fear & Greed Index, Backtrader framework. Load historical via CCXT, define DCA with MACD + Fear & Greed parameters. |
| **Scalping M15 Gold** | EMA14, RSI14, MACD 15-35-9, Stoch, BB, VWAP trend filter. Tighter TP/SL & faster entries for active intraday. |
| **Momentum** | MACD line > signal, Volume oscillator positive (short EMA > long EMA), close >50 MA. |
| **BTCUSDT Futures 1m Scalping** | MACD pane for momentum shifts, quick execution, monitor slippage/latency. |

## Role-Based Indicator Approach (Smart Approach)

Biggest mistake: too many indicators. Better role-based:
- Trend → Moving Averages
- Momentum → RSI or MACD
- Volatility & Risk → ATR
- Context → Support & Resistance
When all align, trades become higher probability.

## MACD WITH LE/SE Super Prediction Details

**LE = Long Entry, SE = Short Entry**

Gold Optimized LE: Price >200 EMA + RSI>50 + MACD crosses above Upper Bollinger Band
Gold Optimized SE: Price <200 EMA + RSI<50 + MACD crosses below Lower BB

Super Prediction Logic:
- Fast EMA 5-9 (gold best), Slow 26-35, Signal 9
- MACD_line = Fast - Slow, Signal_line = EMA(MACD,9), Histogram = MACD - Signal
- LE: MACD crosses above zero (BBO Buy), volume oscillator positive, MACD above signal, histogram above zero, zero-line proximity filter + minimum distance filter, price >50-day MA confirmation
- SE: MACD crosses below zero (BBO Sell), volume positive, MACD below signal, close long and enter short
- Exit: Long exit when MACD crosses below signal or RSI<50, Short exit when MACD crosses above signal
- SL: 1.5*ATR or below swing low, TP: 5%/10% Strategy C ($4500 resistance, $4280 support for gold)

BTC Optimized:
- MacNorm normalized main line captures short vs long momentum. Above 0 bullish stronger, below 0 bearish.
- Trigger Line WMA of MacNorm, smooth, lags.
- FastMA period: smaller = more sensitive but more false signals
- SlowMA period: larger = smoother, less false, more lag
- Normalization period: larger = stable, smaller = dynamic but fluctuating
- Moving average types: EMA recent weighted responsive, WMA linear weight, SMA equal weight smoothest
