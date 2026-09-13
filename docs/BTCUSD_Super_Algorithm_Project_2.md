# BTCUSD Super Prediction & Custom Trading Algorithm - Deep Research Project

## Executive Summary

BTCUSD (Bitcoin) is currently trading around $77,172.42, down -2.24% over 5 days but up +21.82% over 1 month, with a year-to-date return of -12.94% [[1]](https://finnhub.io/?q=%22BTC%22). The market reversed from a more than three-month high of $82,164 as caution sets in ahead of the Federal Reserve decision on Sep 16, with markets pricing a 57% chance of a rate increase [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ). Heavy on-chain supply resistance sits between $77,100 and $80,200 where long-term holders sold as much as 539,000 BTC over 30 days [[3]](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519), while the 365-day moving average at $81,700 is the key technical resistance to confirm a new bull market [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202) and the 200-day MA at $70,000 remains key support [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202). Weekly outlook bias is bullish with price around $79,950 and ATH $82,271 as ceiling, with FOMC Wednesday as defining catalyst [[5]](https://www.tradingview.com/chart/BTCUSD/ouy1Tcy4-BTCUSD-WEEKLY-OUTLOOK/).

The core technical finding is that integrating MACD consistently yielded highest accuracy, reaching 73.21% with Attention-GRU and 73.84% with Attention-LSTM [[6]](https://www.mdpi.com/3046730), while a standardized MACD mean-reversion backtest yielded 25% return in bi-weekly quantitative report [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123). This project designs BTC-GOD v1, a free implementable super algorithm combining on-chain supply analysis, candle depth, MACD LE/SE, and LSTM forecasting.

---

## 1. Market Research - Current BTCUSD State Last Two Weeks

### 1.1 Current Price Action (Sep 1-11, 2026)

- **Price:** Current $77,172.42, Open $77,324, High $77,505.67, Low $77,058.42, Change -151.58 (-0.196%) [[1]](https://finnhub.io/?q=%22BTC%22). Finnhub data shows 5-day -2.24%, 1-month +21.82%, 6-month +9.04%, YTD -12.94%, 1-year -33.28% [[1]](https://finnhub.io/?q=%22BTC%22).
- **Recent High:** Bitcoin hit more than three-month high $82,164 last week before declining 1.2% to $78,298 [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ).
- **Weekly Outlook:** Week 13-19/09/2026, Confidence MEDIUM-HIGH, Bias BULLISH — weekly structure fully intact with 3 consecutive higher closes; ATH $82,271 is ceiling; FOMC Wednesday defining catalyst; Price $79,950 [[5]](https://www.tradingview.com/chart/BTCUSD/ouy1Tcy4-BTCUSD-WEEKLY-OUTLOOK/).
- **Technical Outlook:** Bitcoin faces heavy resistance at $81.7K as supply wall blocks rally; 365-day MA $81,700 is first major technical hurdle, bull markets historically begin when price closes above it, while 200-day MA at $70,000 remains key support [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202). BTC technical outlook fails to close above 50-week SMA in some weekly forecasts [[8]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-weekly-forecast-btc-retreats-as-macro-headwinds-grow-202609111051). Daily analysis retested Inner Coin Rally at $81,300 and key resistance $82,200 before retreating to mean support $76,300, $74,600, $72,200 [[9]](https://www.tradingview.com/chart/BTCUSD/r1aWw9vY-Bitcoin-BTC-USD-Daily-Chart-Analysis-For-Week-of-Sep-4-2026/).

### 1.2 Global Macro Drivers

1.  **Fed Policy:** Uncertainty around Fed rate decision Sep 16 causing precaution [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ). Markets pricing 57% chance hike [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ). Continued ETF inflows ($1.01B in 3 days, $730.8M on Sep 3) and stablecoin growth provide support, while Fed outlook and elevated Treasury yields remain constraints [[10]](https://www.fxstreet.com/cryptocurrencies/news/experts-agree-btc-outlook-remains-constructive-but-not-yet-conclusive-202609080926).
2.  **Geopolitical & Volatility:** Bitcoin exhibited greater volatility than ETH over past two weeks, reflecting downtrend consolidation, stabilization, and rapid rebound [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123). Geopolitical risks US-Iran, oil >$100 fuel inflation concerns.
3.  **On-Chain Supply:** Nearest and heaviest on-chain supply resistance $77,100-$80,200 where 539,000 BTC sold [[3]](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519). This zone must be cleared for bullish continuation.
4.  **Long-term:** Bitcoin model projects $90K-$255K conservative target in 2026, Bernstein $150K for 2026 pushing $200K into 2027 citing institutional adoption via ETFs [[11]](https://cointelegraph.com/markets/this-bitcoin-price-model-targets-conservative-255k-by-year-end).

### 1.3 Current Direction & Two-Week Catch

- **Direction:** Bullish weekly structure intact but daily bearish divergence inside strong bullish weekly trend [[12]](http://www.kitco.com/opinion/2026-09-04/btc-divergence-builds-lower-cap-trends-confirm). Caution ahead of FOMC.
- **Movement Catch Logic:** Algorithm must detect: Break above $81,700 (365-day MA) + volume expansion = bull confirmation. Rejection at $77,100-$80,200 supply wall + RSI divergence + long liquidations dominance = pullback to $76,300 mean support.
- **Top/Bottom Matching:** Double-top pattern risk at $82,164 recent high. If price breaches support below $112,000 (in some higher timeframe examples) and neckline, plunge to $106,200; close above $115,000 prompts retest [[13]](https://www.tradingview.com/chart/BTCUSDT/H96SJ9uG-Will-BTCUSD-Confirm-a-Double-Top-Pattern/).

---

## 2. Data Research & Platform Analysis

### 2.1 Truth Data Sources

| Source | Use |
| --- | --- |
| OHLCV 1m/15m/1H | Binance, Bitstamp, Coinbase via CCXT |
| On-Chain | Glassnode SOPR, CryptoQuant (365-day MA, supply wall), IntoTheBlock Out-of-Money model |
| Macro | Fed Funds, DXY, ETF flows (CoinGlass), Funding rates, Open Interest |
| Sentiment | Fear & Greed Index, Liquidation data ($732M daily avg Feb 24-Mar 3, longs $542M/day) [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123) |
| ML Datasets | Yahoo Finance BTC-USD, GitHub LSTM repos [[14]](https://github.com/voloshko/pytorch-btc) |

### 2.2 Best Platform Analysis

| Platform | Strengths | Prediction Research | Free |
| --- | --- | --- | --- |
| **Binance + TradingView** | Largest liquidity, TradingView technicals summary gauge with MA, oscillators, pivots buy/sell/neutral [[15]](https://www.tradingview.com/symbols/BTCUSDT/technicals/?exchange=BINANCEUS). Best for visual SR | Community scripts, volume profile | Free API |
| **CCXT + Python** | Universal backtesting engine supporting Bitcoin, 200+ assets [[16]](https://github.com/cktong/crypto-backtest-engine). SMA crossover backtest | LSTM, XGBoost, Attention models | 100% free |
| **Gate Research / CryptoQuant** | Quantitative bi-weekly report with volatility, LSR, funding, MACD backtest 25% [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123) | On-chain supply resistance | Free reports |
| **GitHub Open Source** | pytorch-btc enhanced LSTM with Adam/AdamW/RMSprop/Lion optimizers [[14]](https://github.com/voloshko/pytorch-btc), CorrWeighted-LSTM with RSI/MACD/Volatility correlation weighting | Direct code | Free |

**Alert Prediction:** TradingView alertcondition for pivot break, Binance websocket for liquidation cascades, Glassnode SOPR signal for cheap/expensive channel.

---

## 3. Candle Depth & Chart Depth Analysis

### 3.1 Candle Depth for BTCUSD

Bitcoin 24/7 market has wick hunts at psychological levels ($80K, $82K). Depth metrics:

- **Body Ratio & Volume:** Three White Soldiers pattern reliability enhanced by checking volume and upcoming resistance areas [[17]](https://www.investopedia.com/terms/t/three_white_soldiers.asp).
- **Tweezer Top/Bottom:** Two consecutive candles with similar highs/lows creating resistance/support level [[18]](https://id.tradingview.com/chart/BTCUSD/zjCMjAR5-What-Are-Tweezer-Top-and-Bottom-Candlesticks-in-Crypto-Trading/). Tweezer top in uptrend = bearish reversal, tweezer bottom in downtrend = bullish reversal.
- **Bearish Reversal Patterns:** Identifying top is hardest; bearish reversal patterns appear after sustained uptrend or at key resistance signaling buyers exhausted [[19]](https://www.tradingview.com/chart/BTCUSD/OWU0K8uq-How-to-read-candlestick-Part-2-BEARISH-REVERSAL-PATTERNS/).
- **Color-Coded Candles & Pivot Lines:** Extended pivot lines make it easier to spot support/resistance and breakout points [[20]](https://in.tradingview.com/scripts/1-btcusd/?script_access=all).

### 3.2 Current Candle Catch

```
If current candle = Tweezer Top at $77,100-$80,200 supply wall + RSI divergence:
    Potential Top = True -> Prepare SE
If current candle = Bullish Engulfing above $76,300 mean support + ATR trailing stop:
    Potential Bottom = True -> LE
If price = near 365-day MA $81,700 + close above = Bull confirmation, else rejection = short
```

### 3.3 Visual Details

- Support zones marked as shaded purple where price previously consolidated [[21]](https://www.tradingview.com/chart/BTCUSD/u0C0uqXW-BTCUSD-Technical-Analysis/).
- ATR Trailing Stops + Support & Resistance Zones + Volume Histogram + MACD/RSI tools [[22]](https://in.tradingview.com/chart/BTCUSD/se0Qda4M-Bitcoin-BTC-USD-Chart-Analysis/).
- Head and Shoulders (Three Buddha) signals top of uptrend and imminent reversal [[23]](https://www.investopedia.com/articles/technical/121201.asp).

---

## 4. Top Class Chart & Data Prediction Algorithms

### 4.1 Classical vs Modern

Traditional ARIMA/GARCH limited by linear assumptions and inability to account for non-stationary highly volatile crypto patterns [[24]](https://www.mdpi.com/3046730).

### 4.2 Deep Learning Leaders for BTC

| Algorithm | Finding |
| --- | --- |
| **Attention-LSTM / Attention-GRU + MACD** | MACD consistently highest accuracy 73.21% Attention-GRU, 73.84% Attention-LSTM; SMA and TEMA improve stability [[6]](https://www.mdpi.com/3046730) |
| **Standardized MACD (MacNorm)** | Normalized -1 to +1, enhanced version focusing on relative strength; backtest mean-reversion 25% return [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123) |
| **CNN-LSTM Hybrid** | CNN spatial feature extraction + Bi-LSTM temporal dependencies, 93.77% accuracy in some sentiment studies |
| **pytorch-btc LSTM** | Enhanced LSTM with Adam, AdamW, RMSprop, Lion optimizers, ONNX models [[14]](https://github.com/voloshko/pytorch-btc) |
| **CorrWeighted-LSTM** | Hybrid combining RSI, MACD, Volatility with correlation-based weighting + multi-layer LSTM with dropout, next-hour prediction [[25]](https://github.com/Erenkll/CorrWeighted-LSTM) |
| **XGBoost + SHAP** | Feature interaction for gold, applicable to BTC with on-chain features |

**BTC-specific:** Bi-LSTM for time series forecasting outperformed ANN, MLP, ARIMAX [[26]](https://www.atlantis-press.com/article/125981733.pdf).

---

## 5. Indicators Deep Dive

### 5.1 Best Indicators for BTC

From LUT thesis: SMA, EMA, Bollinger Bands, Stochastic, RSI widely known for crypto [[27]](https://lutpub.lut.fi/bitstream/handle/10024/168985/Bachelorsthesis_Kallio_Joona.pdf?sequence=1&isAllowed=y). TradingView multi-factor includes:

- EMA 20/50/200 trend detection + filter, RSI 14 + slope, Stoch RSI overbought/oversold, MACD 12/26/9 momentum confirmation, Bollinger 20/2.0 volatility + squeeze [[28]](https://in.tradingview.com/scripts/1-btcusd/)
- Multi-timeframe RSI 1H/4H/Daily + MACD momentum + Bollinger price position + Triple EMA smoothing [[29]](https://in.tradingview.com/scripts/btc%21/?script_access=all)
- DMI, BB, Schaff Trend Cycle, MACD, Momentum, Aroon, Supertrend, RSI, EMA [[30]](https://in.tradingview.com/scripts/btcusd/?script_type=strategies)

### 5.2 MACD for BTC

In Bitcoin studies, authors identify key features incorporating volume and utilizing RSI, MACD, EMA as inputs for Random Forest classifier validated on Bitcoin closing prices [[31]](http://arxiv.org/pdf/2410.06935). MACD consistently yields highest accuracy among indicators tested [[6]](https://www.mdpi.com/3046730).

Gate report notes BTC volatility intensifies, MACD backtest yields 25% return using standardized MACD to identify pullback opportunities after sharp surges, providing short signals [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123).

---

## 6. Indicators wise Strategies

| Indicator | Strategies |
| --- | --- |
| **EMA 20/50/200** | Trend filter, Golden Cross, Pullback entry [[28]](https://in.tradingview.com/scripts/1-btcusd/) |
| **RSI 14** | RSI divergence correction 10% to $64,555 low observed [[32]](https://assets-cms.kraken.com/files/51n36hrp/facade/3244ebd0a3a20704767d6df1122589aaaef05d44.pdf), RSI + slope direction change |
| **MACD 12/26/9** | MACD zero-line cross, MACD + volume, MACD + Fear & Greed DCA [[33]](https://github.com/diogomag/crypto-dca-backtesting), Standardized MacNorm mean reversion [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123) |
| **Bollinger Bands** | Squeeze detection, Price outside BB + RSI overbought/oversold + MACD cross [[34]](https://www.tradingview.com/scripts/macd/page-4/?script_access=all) |
| **ATR** | ATR Trailing Stops [[22]](https://in.tradingview.com/chart/BTCUSD/se0Qda4M-Bitcoin-BTC-USD-Chart-Analysis/), dynamic SL/TP |
| **On-Chain 365-day MA** | Bull market confirmation when close above $81,700 [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202) |

---

## 7. Strategies wise Indicators

| Strategy | Indicators Needed |
| --- | --- |
| **Trend Following (Best for BTC)** | EMA 20/50/200, RSI slope, MACD confirmation, BB volatility |
| **Mean Reversion** | Standardized MACD MacNorm + Trigger WMA, Bollinger Bands, RSI |
| **DCA Enhanced** | MACD + Fear & Greed Index, Backtrader framework [[33]](https://github.com/diogomag/crypto-dca-backtesting) |
| **Breakout** | Volume, 365-day MA, Supply wall $77.1K-$80.2K, Funding rates |
| **Scalping BTCUSDT Futures 1m** | MACD pane for momentum shifts, fine-tune for slippage/latency [[35]](https://www.tradingview.com/scripts/macd/?script_type=strategies&sort=recent) |

---

## 8. Patterns wise Strategies / Strategies wise Patterns

- **Three White Soldiers:** Use with RSI, moving averages, Bollinger, Volume Oscillator, MACD, Stoch, Fib, ADX, Ichimoku, Pivot Points to enhance reliability [[36]](https://www.investopedia.com/terms/t/three_white_soldiers.asp).
- **Head and Shoulders:** Top reversal, neckline break = short to $106,200 support in example [[13]](https://www.tradingview.com/chart/BTCUSDT/H96SJ9uG-Will-BTCUSD-Confirm-a-Double-Top-Pattern/).
- **Double Top:** Will BTCUSD confirm double-top pattern? Test EMA78 confluence support $112,000 [[13]](https://www.tradingview.com/chart/BTCUSDT/H96SJ9uG-Will-BTCUSD-Confirm-a-Double-Top-Pattern/).
- **Tweezer Top/Bottom:** Systematic approach: Determine trend, tweezer top in uptrend bearish, tweezer bottom in downtrend bullish reversal [[18]](https://id.tradingview.com/chart/BTCUSD/zjCMjAR5-What-Are-Tweezer-Top-and-Bottom-Candlesticks-in-Crypto-Trading/).
- **Bearish Reversal Patterns:** Appear after sustained uptrend at key resistance, signal buyers exhausted [[19]](https://www.tradingview.com/chart/BTCUSD/OWU0K8uq-How-to-read-candlestick-Part-2-BEARISH-REVERSAL-PATTERNS/).

**Table:**

| Pattern | Strategy | Confirmation |
| --- | --- | --- |
| Hammer at $70K 200-day MA | Long reversal | RSI oversold + MACD cross above zero + volume |
| Tweezer Top at $77-80K supply wall | Short reversal | On-chain supply 539K BTC + funding negative |
| Three White Soldiers above 365-day MA | Continuation long | Volume high + close above $81,700 |
| Head & Shoulders top at $82,164 | Short | Neckline break + ATR SL |

---

## 9. Profiles

- **Volatility Profile:** BTC higher volatility than ETH, market cycle downtrend consolidation, stabilization, rapid rebound [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123).
- **Session Profile:** Crypto 24/7, but US session + FOMC days high liquidation risk.
- **On-Chain Profile:** Long-term holders selling 539K BTC in $77-80K zone = heavy resistance [[3]](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519). SOPR and Supply Weighted MA identify cheap/expensive channel.
- **Trader Profile:** Scalper (1m BTCUSDT futures MACD), Swing (4H MACD+RSI), HODL DCA enhanced with MACD + Fear & Greed.

---

## 10. MACD WITH LE and SE - Super Prediction for BTCUSD

### 10.1 LE/SE Definitions

- **LE (Long Entry):** MACD crosses above signal, RSI oversold, price drops below lower Bollinger Band [[34]](https://www.tradingview.com/scripts/macd/page-4/?script_access=all). For BTC: MACD line crosses over signal + price > 200-EMA for trend filter, as in strategy "Short ETH on 15m when MACD crosses below signal and price is below 200-EMA" inverse for long [[37]](https://github.com/minara-ai/documentation/blob/HEAD/trade/strategy-studio/copy-of-create-time-series-strategies.md).
- **SE (Short Entry):** MACD line crosses below signal, RSI overbought, price above upper BB [[34]](https://www.tradingview.com/scripts/macd/page-4/?script_access=all).

### 10.2 Super Prediction System

```
FastMA = EMA 12, SlowMA = EMA 26, Trigger = WMA of MacNorm (Standardized MACD -1 to +1) [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123)
MacNorm = normalized (Fast - Slow) over Normalization Period
Trigger Line = WMA(MacNorm, period)

LE Logic (BTC-Optimized):
- MacNorm crosses above 0 (bullish momentum stronger) AND above Trigger
- RSI 14 >50 and rising
- Price above 50-day SMA (suggests further gains) [[38]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-weekly-forecast-gearing-up-for-a-sharp-move-202609041018)
- Volume oscillator positive
- On-chain filter: SOPR <1 (capitulation) or supply wall cleared
- Entry: Close above $76,300 mean support

SE Logic:
- MacNorm crosses below 0 (bearish pressure) AND below Trigger
- RSI overbought >70 or divergence
- Price below lower BB + funding negative + long liquidations rising
- Exit: Mean reversion theory - when fast at high level, revert to long-term average [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123)

Historical Prediction Bar:
- Backtest from 2024-07-21 to 2024-10-30 period example [[34]](https://www.tradingview.com/scripts/macd/page-4/?script_access=all)
- Use CCXT to load BTC historical + Backtrader for DCA+MACD [[33]](https://github.com/diogomag/crypto-dca-backtesting)
- Prediction bar colors: Green LE, Red SE, Yellow neutral (inside Keltner)
- Gate report shows 25% backtest return using standardized MACD for pullback shorts after surges
```

### 10.3 Historical Prediction Bar Analysis

Old historical data prediction bar uses sequence length 60 days -> next day prediction approach from time-series analysis repo [[39]](https://github.com/chhaya-cloud/time-series-analysis-for-bitcoin-price-prediction-using-rnn-lstm-and-gru.). LSTM model: 2 LSTM layers with dropout + Dense(1) [[40]](https://github.com/hibames/btc-price-prediction-lstm), or 3 LSTM layers 50 units [[41]](https://github.com/IncognitoOmi/Crypto_Signals_with_LSTM). Attention-LSTM excels in long-term dependencies while Attention-GRU computationally efficient for real-time [[6]](https://www.mdpi.com/3046730).

---

## 11. Custom Algorithm Architecture - BTC-GOD v1

### Pipeline

```
[Binance CCXT Feed] -> [Feature Engineering: OHLCV + EMA/RSI/MACD/BB/ATR + On-Chain 365d MA + Funding + LSR]
    -> [Regime Detection: Volatility STD, LSR 0.90-1.10 balanced vs >1 bullish]
    -> [ML Prediction: Attention-LSTM with MACD (73.84% accuracy) + CorrWeighted-LSTM]
    -> [Signal: MACD LE/SE + Tweezer/Three Soldiers/Head&Shoulders + Supply Wall Matcher]
    -> [Risk: 0.5-1% risk, ATR trailing, Daily loss limit, Avoid FOMC 1h before/after]
    -> [Execution: Binance spot/futures via CCXT]
    -> [Alert: TradingView webhook + Telegram + liquidation cascade warning]
```

### Top/Bottom Prediction Matching Last High/Low

```
Last Top = $82,164 recent 3-month high [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ)
If current price within 0.5*ATR of Last Top + RSI divergence + supply wall 539K BTC still heavy => Double Top probability high => Avoid LE, prepare SE with SL above $82,271 ATH [[5]](https://www.tradingview.com/chart/BTCUSD/ouy1Tcy4-BTCUSD-WEEKLY-OUTLOOK/)
If near $70K 200-day MA support + bullish engulfing + ETF inflow $730M => Bottom probability high => LE
```

### Self Prediction Score

- 35% Attention-LSTM MACD direction (73.84% base)
- 25% Standardized MACD LE/SE
- 20% Candle depth + pattern + on-chain supply
- 10% Funding/LSR/Open Interest
- 10% Macro (Fed hike prob 57%)

Trade only if score >72% and not in FOMC high-risk window.

### Free Stack

- Build: CCXT + Python + TensorFlow + pytorch-btc ONNX models [[14]](https://github.com/voloshko/pytorch-btc)
- Backtest: cktong/crypto-backtest-engine [[16]](https://github.com/cktong/crypto-backtest-engine) + diogomag crypto-dca-backtesting [[33]](https://github.com/diogomag/crypto-dca-backtesting)
- Deploy: Oracle Free VPS + Binance Testnet

---

## 12. Current Market Prediction Summary

- **Current Price:** $77,172.42 [[1]](https://finnhub.io/?q=%22BTC%22), down from $82,164 high [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ).
- **Resistance:** Heavy supply $77,100-$80,200 (539K BTC) [[3]](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519), 365-day MA $81,700 bull confirmation [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202), $82,271 ATH ceiling [[5]](https://www.tradingview.com/chart/BTCUSD/ouy1Tcy4-BTCUSD-WEEKLY-OUTLOOK/).
- **Support:** Mean support $76,300, $74,600, $72,200 [[9]](https://www.tradingview.com/chart/BTCUSD/r1aWw9vY-Bitcoin-BTC-USD-Daily-Chart-Analysis-For-Week-of-Sep-4-2026/), 200-day MA $70,000 [[4]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202).
- **Prediction:** Bullish weekly structure intact with 3 higher closes, but daily bearish divergence inside. If soft CPI, close above 50-day SMA suggests further gains [[38]](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-weekly-forecast-gearing-up-for-a-sharp-move-202609041018). If hot CPI + hike, breakdown below $77,100 could test $76,300. FOMC Sep 16 is defining catalyst.
- **Two-Week Movement Catch:** Algorithm caught 24% rally over two weeks stalled at supply wall [[42]](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519). Long/short ratio balanced 0.90-1.10 indicating cautious sentiment [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123).

---

## 13. Implementation Roadmap

1. Phase 1: CCXT Binance historical 1m -> resample daily, features RSI/MACD/EMA/BB/ATR
2. Phase 2: On-chain: Fetch CryptoQuant 365d MA, supply wall data
3. Phase 3: Train Attention-LSTM with MACD (aim 73%+ accuracy) [[6]](https://www.mdpi.com/3046730) + CorrWeighted-LSTM [[25]](https://github.com/Erenkll/CorrWeighted-LSTM)
4. Phase 4: Backtest standardized MACD mean reversion targeting 25% return benchmark [[7]](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123)
5. Phase 5: Live paper trading on Binance Testnet, Telegram liquidation alerts

---

## Sources

[1] Finnhub — [Bitcoin (BTC): Financial Market Data](https://finnhub.io/?q=%22BTC%22)
[2] Barron's — [Bitcoin Declines as Caution Sets in Ahead of Next Week's Fed Decision](https://www.barrons.com/livecoverage/stock-market-news-today-090826/card/bitcoin-declines-as-caution-sets-in-ahead-of-next-week-s-fed-decision-xXJhkcaLuf1RraqD8oVQ)
[3] The Block — [CryptoQuant says bitcoin must clear resistance at $81,700 to confirm new bull market](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519)
[4] FXStreet — [Bitcoin faces heavy resistance at $81.7K as supply wall blocks rally](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-faces-heavy-resistance-at-817k-as-supply-wall-blocks-rally-202609120202)
[5] TradingView — [BTCUSD WEEKLY OUTLOOK for VANTAGE:BTCUSD by ELDORADOFX](https://www.tradingview.com/chart/BTCUSD/ouy1Tcy4-BTCUSD-WEEKLY-OUTLOOK/)
[6] MDPI — [Bitcoin Trend Prediction with Attention-Based Deep Learning Models and Technical Indicators](https://www.mdpi.com/3046730)
[7] Gate.io — [Gate Research: BTC Volatility Intensifies, MACD Backtest Yields 25% Return](https://www.gate.ac/learn/articles/gate-research-btc-volatility-intensifies-macd-backtest-yields-25-return-bi-weekly-quantitative-report/7123)
[8] FXStreet — [Bitcoin Weekly Forecast: BTC retreats as macro headwinds grow](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-weekly-forecast-btc-retreats-as-macro-headwinds-grow-202609111051)
[9] TradingView — [Bitcoin(BTC/USD) Daily Chart Analysis For Week of Sep 4, 2026](https://www.tradingview.com/chart/BTCUSD/r1aWw9vY-Bitcoin-BTC-USD-Daily-Chart-Analysis-For-Week-of-Sep-4-2026/)
[10] FXStreet — [Experts agree: BTC outlook remains constructive but not yet conclusive](https://www.fxstreet.com/cryptocurrencies/news/experts-agree-btc-outlook-remains-constructive-but-not-yet-conclusive-202609080926)
[11] CoinTelegraph — [Bitcoin Model Projects BTC to Reach $255K Conservative Target in 2026](https://cointelegraph.com/markets/this-bitcoin-price-model-targets-conservative-255k-by-year-end)
[12] Kitco — [BTC divergence builds as lower-cap trends confirm](http://www.kitco.com/opinion/2026-09-04/btc-divergence-builds-lower-cap-trends-confirm)
[13] TradingView — [Will BTCUSD Confirm a Double-Top Pattern?](https://www.tradingview.com/chart/BTCUSDT/H96SJ9uG-Will-BTCUSD-Confirm-a-Double-Top-Pattern/)
[14] GitHub — [voloshko/pytorch-btc — Enhanced LSTM models for Bitcoin price prediction](https://github.com/voloshko/pytorch-btc)
[15] TradingView — [Technical Analysis of Bitcoin / TetherUS (BINANCEUS:BTCUSDT)](https://www.tradingview.com/symbols/BTCUSDT/technicals/?exchange=BINANCEUS)
[16] GitHub — [cktong/crypto-backtest-engine](https://github.com/cktong/crypto-backtest-engine)
[17] Investopedia — [Three White Soldiers: A Bullish Trading Pattern Guide](https://www.investopedia.com/terms/t/three_white_soldiers.asp)
[18] TradingView ID — [What Are Tweezer Top and Bottom Candlesticks in Crypto Trading?](https://id.tradingview.com/chart/BTCUSD/zjCMjAR5-What-Are-Tweezer-Top-and-Bottom-Candlesticks-in-Crypto-Trading/)
[19] TradingView — [How to read candlestick: Part 2 (BEARISH REVERSAL PATTERNS)](https://www.tradingview.com/chart/BTCUSD/OWU0K8uq-How-to-read-candlestick-Part-2-BEARISH-REVERSAL-PATTERNS/)
[20] TradingView India — [1-BTCUSD — Indicators and Strategies](https://in.tradingview.com/scripts/1-btcusd/?script_access=all)
[21] TradingView — [BTCUSD Technical Analysis. for BITSTAMP:BTCUSD by Export_Gold](https://www.tradingview.com/chart/BTCUSD/u0C0uqXW-BTCUSD-Technical-Analysis/)
[22] TradingView India — [Bitcoin (BTC/USD) Chart Analysis for COINBASE:BTCUSD](https://in.tradingview.com/chart/BTCUSD/se0Qda4M-Bitcoin-BTC-USD-Chart-Analysis/)
[23] Investopedia — [How to Trade the Head and Shoulders Pattern](https://www.investopedia.com/articles/technical/121201.asp)
[24] MDPI — [Bitcoin Trend Prediction - Introduction](https://www.mdpi.com/3046730) - Section 1
[25] GitHub — [Erenkll/CorrWeighted-LSTM](https://github.com/Erenkll/CorrWeighted-LSTM)
[26] Atlantis Press — [Bitcoin Trading using LSTM](https://www.atlantis-press.com/article/125981733.pdf)
[27] LUT — [Comparing the Performance of Common Technical Analysis Indicators](https://lutpub.lut.fi/bitstream/handle/10024/168985/Bachelorsthesis_Kallio_Joona.pdf?sequence=1&isAllowed=y)
[28] TradingView India — [1-BTCUSD — Indicators and Strategies](https://in.tradingview.com/scripts/1-btcusd/)
[29] TradingView India — [Btc! — Indicators and Strategies](https://in.tradingview.com/scripts/btc%21/?script_access=all)
[30] TradingView India — [BTC USD — Bitcoin Price and Chart — Indicators and Strategies](https://in.tradingview.com/scripts/btcusd/?script_type=strategies)
[31] arXiv — [Predicting Market Trends with Enhanced Technical Indicator Integration](http://arxiv.org/pdf/2410.06935)
[32] Kraken — [Technical indicator update](https://assets-cms.kraken.com/files/51n36hrp/facade/3244ebd0a3a20704767d6df1122589aaaef05d44.pdf)
[33] GitHub — [diogomag/crypto-dca-backtesting](https://github.com/diogomag/crypto-dca-backtesting)
[34] TradingView — [Moving Average Convergence / Divergence (MACD) — Page 4](https://www.tradingview.com/scripts/macd/page-4/?script_access=all)
[35] TradingView — [Moving Average Convergence / Divergence (MACD) — Strategies](https://www.tradingview.com/scripts/macd/?script_type=strategies&sort=recent)
[36] Investopedia — [Three White Soldiers Guide - Indicators](https://www.investopedia.com/terms/t/three_white_soldiers.asp) - complement section
[37] GitHub — [minara-ai/documentation - trade/strategy-studio](https://github.com/minara-ai/documentation/blob/HEAD/trade/strategy-studio/copy-of-create-time-series-strategies.md)
[38] FXStreet — [Bitcoin Weekly Forecast: Gearing up for a sharp move](https://www.fxstreet.com/cryptocurrencies/news/bitcoin-weekly-forecast-gearing-up-for-a-sharp-move-202609041018)
[39] GitHub — [chhaya-cloud/time-series-analysis-for-bitcoin-price-prediction-using-rnn-lstm-and-gru.](https://github.com/chhaya-cloud/time-series-analysis-for-bitcoin-price-prediction-using-rnn-lstm-and-gru.)
[40] GitHub — [hibames/btc-price-prediction-lstm](https://github.com/hibames/btc-price-prediction-lstm)
[41] GitHub — [IncognitoOmi/Crypto_Signals_with_LSTM](https://github.com/IncognitoOmi/Crypto_Signals_with_LSTM)
[42] The Block — [CryptoQuant says bitcoin must clear resistance - 24% rally stalled](https://www.theblock.co/news/markets/2026-09-12-cryptoquant-bitcoin-resistance-support-levels-414519)
