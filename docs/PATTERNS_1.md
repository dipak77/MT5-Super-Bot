# Patterns Documentation

## Candlestick Patterns - Accuracy 50-55% Alone (Needs Filter)

### Single Candle
- **Doji:** Indecision, body ratio <30%. Need volume confirmation.
- **Hammer / Hanging Man:** Long lower wick >2x body, small upper. Hammer at bottom downtrend = potential upward reversal. Hanging man at top = potential down.
- **Gravestone Doji / Shooting Star:** Long upper shadow, no lower, strong resistance. Strong bearish.
- **Strong Bull/Bear:** Body ratio >70% strong momentum.

### Double Candle
- **Bullish Engulfing:** Current closes above previous open and engulfs range, near low pivot within 1% = Long high probability.
- **Bearish Engulfing:** Opposite, near resistance.
- **Tweezer Top/Bottom:** Two consecutive candles with similar highs/lows creating resistance/support. Tweezer top in uptrend bearish reversal, tweezer bottom in downtrend bullish reversal. Systematic approach: Determine trend first.
- **Piercing Line / Dark Cloud**

### Triple Candle
- **Morning Star / Evening Star:** Morning star at $4005.79 signal bottom in gold example. Bullish hammer + morning star pattern at $4005.79.
- **Three White Soldiers:** Three consecutive bullish candles, but need to check volume and upcoming resistance. Use with RSI, moving averages, Bollinger, Volume Oscillator, MACD, Stoch, Fib, ADX, Ichimoku, Pivot Points to enhance reliability.
- **Three Black Crows:** Bearish version.

## Chart Patterns

- **Head and Shoulders (Three Buddha):** Three peaks, middle highest, lows form neckline support = top reversal and imminent reversal. Easily recognizable.
- **Triple Top/Bottom:** Backed by RSI or MACD divergence. Need broader market conditions.
- **Double Top/Bottom:** Will BTCUSD confirm double-top? BTC broke ascending trendline between EMAs, testing EMA78 confluence support $112K. If breaches below $112K and neckline, plunge to $106.2K. Close above $115K retest broken descending trendline.
- **Triangle:** Triangle height ensures meaningful depth, horizontal tolerance controls flat resistance. Ascending, descending, symmetrical.
- **Flag / Pennant**

## Pattern wise Strategies Table

| Pattern | Strategy | Confirmation |
|---------|----------|--------------|
| Hammer at Support (Gold $4005, BTC $70K 200-day MA) | Reversal Long | RSI divergence, EMA21>EMA50, MACD cross above zero, volume spike |
| Bearish Engulfing at Resistance ($81.7K 365-day MA, $4500 gold) | Reversal Short | Volume spike, RSI<50, Close below 21 EMA, funding negative |
| Bullish Engulfing + 200 EMA | Continuation Long | Volume oscillator positive, close above 50 MA, ETF inflow |
| Morning Star at $4005.79 + MFI rising | Bottom Long | MFI rising liquidity, MACD reduced bearish momentum |
| Tweezer Top at $77-80K supply wall (539K BTC) | Short reversal | On-chain supply heavy + funding negative + long liquidations |
| Three White Soldiers above 365-day MA | Continuation Long | Volume high + close above $81,700 + RSI>50 |
| Head & Shoulders top at $82,164 recent high | Short | Neckline break + ATR SL, volume confirmation |
| Gravestone Doji at top + volume spike | Strong resistance Short | ATR SL, wait for confirmation |

## Strategies wise Patterns Table

| Strategy | Patterns to Look For |
|----------|---------------------|
| Reversal Long at Support | Hammer, Bullish Engulfing, Morning Star, Tweezer Bottom |
| Reversal Short at Resistance | Gravestone Doji, Bearish Engulfing, Evening Star, Tweezer Top, Head & Shoulders |
| Continuation Long in Uptrend | Three White Soldiers, Bullish Engulfing above EMA, Flag breakout |
| Top/Bottom Prediction | Double Top/Bottom, Triple Top/Bottom, Head & Shoulders, RSI divergence + pattern |

## Visual Details for Dashboard

- Color-coded candles: Uptrend Blue, Downtrend Red (or green/red)
- Extended pivot lines to spot support/resistance and breakout points
- Shaded zones: Support light blue demand area before breakout, Resistance purple where price previously consolidated
- ATR Trailing Stops + Support & Resistance Zones + Volume Histogram + MACD/RSI tools overlay
- Retest signals: Broken level approached + rejection candle wick >50% range = polarity flip confirmation
- Sweep signals: Price sweeps beyond level 0.3 ATR then closes back with strong reversal

## Candle Depth Analysis in Code

```python
body_ratio = |Close-Open| / (High-Low)
if body_ratio <0.3: doji
elif close>open and ratio>0.7: strong_bull
elif close<open and ratio>0.7: strong_bear
upper_wick = High - max(Open,Close)
lower_wick = min(Open,Close) - Low
if upper_wick > body*2: gravestone
if lower_wick > body*2: hammer
```
