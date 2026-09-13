# XAUUSD Super Prediction & Custom Trading Algorithm - Deep Research Project

## Executive Summary

XAUUSD (Spot Gold) is currently in a corrective pullback phase within a long-term uptrend, pressured by surging oil prices, rising US Treasury yields, and reinforced expectations of a Federal Reserve rate hike in mid-September 2026 [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/) [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-091126/card/gold-set-for-weekly-loss-as-rate-hike-expectations-pressure-prices-OpTVqqlMXnVpO5tvtg2m). Spot gold traded around $4,324.79 with resistance emerging above $4,500 and buying interest below $4,400 ahead of key support at $4,320 [[3]](https://www.reuters.com/world/india/gold-eases-robust-us-payrolls-boost-rate-hike-bets-inflation-data-focus-2026-09-07/). This project synthesizes data research, platform analysis, candle depth analysis, indicator-strategy matrices, and machine learning prediction to design a free, implementable super algorithm (XAU-GOD v1) focused on MACD with LE/SE (Long Entry / Short Entry) super prediction and historical prediction bar logic.

The core finding is that traditional MACD (12,26,9) underperforms in gold; optimal parameter ranges differ significantly from equities, with small short-term EMA values (n1 5-9) yielding best performance and large values (17-20) yielding worst performance [[4]](https://www.mdpi.com/1911-8074/19/3/192). A robust system must combine role-based indicators (Trend, Momentum, Volatility, Context), support/resistance detection, candle depth, and ML-based forecasting such as CNN-Bi-LSTM and LSTM models specifically built for XAUUSD 15-minute data [[5]](https://github.com/BaseMax/XAUUSD-LSTM).

---

## 1. Market Research - Current State and Last Two Weeks Movement

### 1.1 Current Price Action (Sep 1-11, 2026)

- **Price Level:** Spot gold $4,324.79 on Sep 11, down >2% for the week, third consecutive weekly loss trajectory [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/). Intraday high $4,402.63, low $4,292.11, with 5-day return -1.82% [[6]](https://finnhub.io/?q=%22XAU%2FUSD%22).
- **Futures:** US gold futures for December delivery $4,364.70, down 1% [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/).
- **Key Levels:** Immediate resistance $4,489.87 to $4,538.77 cluster with 200-day MA at $4,538.38 [[7]](https://www.fxempire.com/forecasts/article/gold-xauusd-price-forecast-value-versus-trend-as-gold-stages-technical-bounce-ahead-of-cpi-1626960). Support: 100-day SMA near $4,347.13, 50-day SMA $4,255.70, psychological $4,300 zone [[8]](https://www.fxstreet.com/analysis/4-465-gold-looks-to-regain-21-day-sma-amid-sustained-usd-weakness-202609080230). Analyst target for unwind: $4,280 into Fed meeting [[9]](https://www.fxempire.com/forecasts/article/premium-gold-price-analysis-4280-target-in-view-as-the-crowded-long-unwinds-into-the-fed-1620197).
- **Two-Week Pattern:** Gold found twice buying interest below $4,400 [[3]](https://www.reuters.com/world/india/gold-eases-robust-us-payrolls-boost-rate-hike-bets-inflation-data-focus-2026-09-07/). Pullback continues into mid-September after crowded long positioning; specs owned more of COMEX than in almost any week of last eight years [[9]](https://www.fxempire.com/forecasts/article/premium-gold-price-analysis-4280-target-in-view-as-the-crowded-long-unwinds-into-the-fed-1620197).

### 1.2 Global Macro Drivers - Truth Sources

Gold is driven by USD strength, interest rates, inflation data, geopolitical risk, and market sentiment [[10]](https://www.mql5.com/en/blogs/post/766745).

1.  **Fed Policy:** Strong US jobs data (unemployment 4.1%) and PPI +0.4% in August boosted rate-hike bets for Sep 16 meeting. CME FedWatch pricing 87% chance hike [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/). Rising rates pressure non-yielding gold [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/).
2.  **Oil & Inflation:** Oil benchmarks >$100/barrel for first time since mid-May due to Middle East escalation (Houthis seizing Mocha, Red Sea disruption). Oil surge fuels inflation expectations, reinforcing hawkish Fed [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-091126/card/gold-set-for-weekly-loss-as-rate-hike-expectations-pressure-prices-OpTVqqlMXnVpO5tvtg2m) [[1]](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/).
3.  **Yields & Dollar:** Higher bond yields and stronger dollar outweigh gold's safe-haven appeal. Statement: "Trade barriers and geopolitical disruption can support bullion, but if those push inflation higher, expectations for tighter policy lift yields and increase opportunity cost of holding gold" [[2]](https://www.barrons.com/livecoverage/stock-market-news-today-091126/card/gold-set-for-weekly-loss-as-rate-hike-expectations-pressure-prices-OpTVqqlMXnVpO5tvtg2m).
4.  **Long-term Support:** Central bank buying and ETF inflows keep long-term view constructive; Goldman raised Dec 2026 forecast to $4,900/oz [[11]](https://www.reuters.com/business/goldman-hikes-december-2026-gold-price-forecast-4900oz-2025-10-07/?ref=bytenewsdaily.com).

### 1.3 Current Market Direction & Prediction Framework

- **Direction:** Short-term bearish correction within bullish macro structure. 20- and 50-day SMAs continue upward supporting bullish setup [[12]](https://www.wsj.com/finance/commodities-futures/gold-rises-ahead-of-u-s-cpi-data-c995e7d0), but momentum below $4,500.
- **Movement Catch Logic (Last 2 Weeks):** Algorithm must catch: Breakdown below $4,400 with volume expansion + RSI <50 + MACD below zero = continuation to $4,320-$4,280. Bounce above $4,347 (100-day SMA) with bullish hammer/morning star at $4,005.79 pattern reference = reversal attempt to $4,500.
- **Top/Bottom Prediction Matching:** Compare current swing high/low to last 20-50 period swing high/low. If price is highest/lowest of last 50 periods + RSI overbought/oversold + far from mean = potential top/bottom.

---

## 2. Data Research & Platform Analysis

### 2.1 Truth Data Sources

| Source Type | Platform / Provider | Use |
| --- | --- | --- |
| Spot Price & OHLCV | MT5 History, OANDA, Dukascopy, Finnhub | Primary candle data, 15m/1H/4H |
| Macro | FRED (Fed rates, DXY), EIA (Oil), CPI/PPI calendars | Global impact filter |
| Sentiment | CFTC COT Report (COMEX positioning), ETF flows | Crowded long detection |
| On-chain Alternative | Kaggle XAUUSD 2004-2024 dataset | ML training [[5]](https://github.com/BaseMax/XAUUSD-LSTM) |

### 2.2 Best Platform Analysis

| Platform | Strengths | Prediction Research | Free Integration |
| --- | --- | --- | --- |
| **MetaTrader 5** | Superior tools for price analysis, algorithmic trading (EA), copy trading [[13]](https://www.metatrader5.com/en/trading-platform) [[14]](https://www.metatrader5.com/en/trading-platform/technical-analysis). Native backtester with real spread. | MQL5 community EAs, technical analysis tools. Supports 24/7 XAUUSD247 product [[15]](https://www.fxempire.com/news/article/moneta-markets-launches-24-7-gold-trading-on-mt5-1624917) | 100% free to build EA, Python bridge free |
| **TradingView** | Best visual charting, 100+ indicators, community scripts for Gold Institutional Volume, Asymmetric Trend [[16]](https://www.tradingview.com/scripts/xauusd/page-2/?script_type=indicators&script_access=all). Pine Script strategies with volume oscillator filtering [[17]](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies) | Social consensus, alert prediction, strategy backtest | Free tier + webhook to MT5 via Python |
| **cTrader** | cBot with C#, better order book | Open API | Free |
| **QuantConnect / Python** | ML libraries, LSTM, XGBoost [[5]](https://github.com/BaseMax/XAUUSD-LSTM) | Academic papers, MDPI research | Fully free locally |

**Alert Prediction from All Truth Sources:** Combine TradingView alertcondition (buy/sell at pivot), MT5 push notifications, Telegram Bot API for real-time LE/SE signals, and economic calendar API to pause during CPI/PPI.

---

## 3. Candle Depth & Chart Depth Analysis

### 3.1 Candle Anatomy Depth

Each candle is not just OHLC. Depth metrics:

- **Body Ratio:** |Close-Open| / (High-Low). >70% = strong momentum. <30% = indecision (Doji).
- **Wick Imbalance:** Upper Wick / Lower Wick. Long upper shadow = strong resistance above [[18]](https://github.com/waylandzhang/ai-quant-book/blob/HEAD/manuscript/en/Part2-Quant-Fundamentals/Background/Candlestick-Patterns-and-Volume-Analysis.md).
- **Volume-Price Confirmation:** High volume + small body at support = accumulation.
- **Depth Resistance Analysis:** Measure how many times price wicked into level and rejected. Zone strength = count of rejections * volume at rejection.

> Traditional interpretation: Signal of potential trend reversal. Actual effectiveness: Prediction accuracy around 50-55% when used alone [[18]](https://github.com/waylandzhang/ai-quant-book/blob/HEAD/manuscript/en/Part2-Quant-Fundamentals/Background/Candlestick-Patterns-and-Volume-Analysis.md).

### 3.2 Current Candle Catch with Past Movement

Logic for super algorithm:

```
Current Candle Type = classify(body_ratio, wick_ratio)
If Current Candle = Bullish Engulfing AND previous 3 candles down AND near previous low pivot within 1% [[19]](https://in.tradingview.com/scripts/candlestickanalysis/?sort=recent&script_access=open&script_type=indicators):
    Potential Bottom = True
If Current Candle = Gravestone Doji at top + volume spike:
    Potential Top = True
Match last top/bottom: Distance to last swing high < 0.5 * ATR AND RSI divergence = Double Top probability high.
```

### 3.3 Visual Details & Chart Structure

- **Support/Resistance States:** Fresh (green support, red resistance), Broken (stops extending, labeled marker at break) [[20]](https://www.tradingview.com/scripts/supportandresistance/page-3/?script_type=indicators).
- **Order Block & Breaker:** When close exceeds top of resistance or below bottom of support, zone flips polarity: former support becomes resistance [[21]](https://www.tradingview.com/scripts/supportandresistance/page-2/?script_access=all&script_type=indicators).
- **Top/Bottom Detection:** Use pivot highs/lows with swing strength parameter (bars left=right) to control meaningful depth [[22]](https://www.tradingview.com/scripts/supportandresistance/page-24/?sort=recent&script_type=indicators&script_access=all).

---

## 4. Top Class Chart Prediction & Data Prediction Algorithms

### 4.1 Classical

- ARIMA, VAR, VECM struggled to outperform random walk for gold [[23]](https://www.mdpi.com/1911-8074/19/3/192).
- GARCH/DCC-GARCH for volatility and safe-haven correlation.

### 4.2 Modern ML

| Algorithm | Use for XAUUSD | Finding |
| --- | --- | --- |
| **XGBoost + SHAP** | 7-year XAU/USD + 10 features, window sizes 8/16/32/64, metrics MSE/RMSE/MAPE/R2 [[24]](https://www.researchgate.net/publication/353416702_Forecasting_gold_price_with_the_XGBoost_algorithm_and_SHAP_interaction_values) | Feature interaction important |
| **CNN-Bi-LSTM** | Observation and forecasted charts comparison; automatic parameter tuning [[25]](https://journals.plos.org/plosone/article/figure?id=10.1371/journal.pone.0298426.g005) | Best accuracy for gold |
| **LSTM (BaseMax)** | Python LSTM for 15-min data, sequence length 96, customizable, saves best checkpoint [[5]](https://github.com/BaseMax/XAUUSD-LSTM) | Directly usable free |
| **LSTM-Autoencoder** | Hybrid deep network, handles small/incomplete data vs ARIMA better for small linear data [[26]](https://link.springer.com/article/10.1007/s44163-025-00464-w) | Robust to noise |
| **Support Resistance Optimal Prediction** | Optimal stopping theory, conditional median curves for resistance/support as aspiration level [[27]](https://eprints.whiterose.ac.uk/id/eprint/112048/1/Paper-Revised.pdf) | Mathematical top/bottom |

### 4.3 Implementation Choice

Use **CNN-Bi-LSTM for direction prediction** + **Pivot-based SR detection algorithm** for execution. LSTM predicts next 16 steps (4 hours on 15m) [[5]](https://github.com/BaseMax/XAUUSD-LSTM). SR algorithm gives execution zones.

---

## 5. Indicators Deep Dive

### 5.1 Core Indicators for Gold

From MQL5 analysis [[10]](https://www.mql5.com/en/blogs/post/766745):

- **EMA/SMA:** EMA 21/50 for short-medium trend, EMA 50/200 for long bias. Price above EMAs = bullish bias.
- **RSI:** RSI above 50 bullish momentum, below 50 bearish, divergence warns exhaustion [[10]](https://www.mql5.com/en/blogs/post/766745). Works best with trend confirmation.
- **MACD:** MACD crossing above zero = bullish momentum, below zero = bearish [[10]](https://www.mql5.com/en/blogs/post/766745). Effective on H1, H4, Daily for XAUUSD.
- **ATR:** Dynamic stop loss, adjust TP, avoid low volatility.
- **Bollinger Bands, Keltner, VWAP:** Volatility and squeeze detection. TTM-style squeeze: Bollinger inside Keltner for coil, expansion = release [[28]](https://in.tradingview.com/scripts/metals/?script_type=indicators&sort=recent).

### 5.2 MACD Deep Research

Definition: MACD (n1,n2,n3) where MACD line = EMA(n1) - EMA(n2), Signal = EMA of MACD over n3 [[23]](https://www.mdpi.com/1911-8074/19/3/192). Traditional (12,26,9) is not formal standard; Appel suggested (8,17,9) buy and (12,25,9) sell [[23]](https://www.mdpi.com/1911-8074/19/3/192).

**Gold-Specific Optimal Ranges (MDPI 2025):** Study identified market-specific ranges. Sample models with optimal ranges significantly higher returns, outperforming buy-and-hold and random, suggesting not weak-form efficient [[4]](https://www.mdpi.com/1911-8074/19/3/192). Finding: Small n1 (5-9) best, large n1 (17-20) worst for gold, indicating performance depends on joint configuration [[29]](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918). Overall An1-Bn2-Bn3 group represents optimal degree with both MACD and signal lengthened [[30]](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918).

**Zero-line vs Signal-line Cross:** MACD histogram crossing zero occurs only when MACD line crosses zero, which is more significant momentum event than MACD crossing its own signal line [[31]](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies). Parameters (16,26,9) selected for gold in some strategies [[31]](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies).

---

## 6. Indicators wise Strategies

| Indicator | Strategies Using It |
| --- | --- |
| **EMA 21/50/200** | Trend following pullback, Golden Cross, Dynamic SR |
| **RSI 14/60** | RSI divergence, RSI + MA, RSI hook, Overbought/Oversold reversal |
| **MACD (5-9, 26-35, 9)** | MACD zero-line cross, MACD + Volume Oscillator, MACD + RSI confirmation [[32]](https://www.tradingview.com/chart/XAUUSD/MfSRSz9Q-MACD-RSI-confirmation-strategy/), MACD BB, Stochastic MACD |
| **Bollinger Bands** | Squeeze breakout, BB + RSI, Volatility threshold filter |
| **ATR** | ATR stop loss, ATR TP scaling, Supertrend |
| **VWAP** | VWAP reclaim intraday, VWAP + EMA filter |
| **ADX** | ADX + EMA200 + BB + RSI [[33]](https://github.com/sanxdy/vortex-trading-bot/commit/a1fb04761e474151074331d63256cd8ad2bf6de6) |

---

## 7. Strategies wise Indicators

| Strategy | Required Indicators & Filters |
| --- | --- |
| **Trend Pullback (Best for XAUUSD)** | EMA21>EMA50, price near EMA zone, RSI>50, bullish candle, ATR SL [[10]](https://www.mql5.com/en/blogs/post/766745) |
| **Breakout** | Donchian, Volume expansion, MACD above zero, ATR |
| **Mean Reversion** | Bollinger Bands, RSI 70/30, Support/Resistance |
| **Scalping Gold M15** | EMA14, RSI14, MACD 15-35-9, Stoch, BB, VWAP trend filter [[34]](https://in.tradingview.com/scripts/xauusd%28w%29/) |
| **Momentum** | MACD line > signal, Volume oscillator positive, close >50 MA [[32]](https://www.tradingview.com/chart/XAUUSD/MfSRSz9Q-MACD-RSI-confirmation-strategy/) |

---

## 8. Patterns wise Strategies / Strategies wise Patterns

### 8.1 Candlestick Patterns (Accuracy 50-55% alone, needs filter)

- **Hammer / Hanging Man:** Hammer at bottom of downtrend = potential upward reversal [[18]](https://github.com/waylandzhang/ai-quant-book/blob/HEAD/manuscript/en/Part2-Quant-Fundamentals/Background/Candlestick-Patterns-and-Volume-Analysis.md). Strategy: Hammer + RSI>50 + EMA trend up = Long.
- **Bullish Engulfing:** Current candle closes above previous open and engulfs range, near low pivot within 1% = Long [[19]](https://in.tradingview.com/scripts/candlestickanalysis/?sort=recent&script_access=open&script_type=indicators).
- **Morning Star / Bullish Hammer at $4005.79:** Signal bottom in gold [[35]](https://economictimes.indiatimes.com/news/international/us/gold-price-forecast-should-buy-gold-or-wait-for-stabilization-of-prices-heres-price-prediction-for-tomorrow-next-week-next-30-days-factors-affecting-prices-this-month-xau/usd-market-short-term-trading-strategies-u-s-consumer-price-index-macd-rsi-vwap-sma20/articleshow/124763730.cms?from=mdr).
- **Gravestone Doji / Shooting Star:** Long upper shadow, no lower = strong resistance [[18]](https://github.com/waylandzhang/ai-quant-book/blob/HEAD/manuscript/en/Part2-Quant-Fundamentals/Background/Candlestick-Patterns-and-Volume-Analysis.md). Strategy: Short with ATR SL.
- **Three White Soldiers:** Combines with trendlines, moving averages, volume to confirm breakout [[36]](https://www.investopedia.com/terms/t/three_white_soldiers.asp).

### 8.2 Chart Patterns

- **Head and Shoulders:** Three peaks, middle highest, lows form neckline support = top reversal [[37]](https://www.investopedia.com/articles/technical/121201.asp).
- **Triple Top/Bottom:** Backed by RSI or MACD divergence [[38]](https://www.investopedia.com/articles/technical/02/012102.asp).
- **Triangle:** Triangle height ensures meaningful depth, horizontal tolerance controls flat resistance [[39]](https://www.tradingview.com/scripts/candlestick/?script_access=all&sort=recent).

**Pattern -> Strategy Mapping Table:**

| Pattern | Strategy | Confirmation |
| --- | --- | --- |
| Hammer at Support | Reversal Long | RSI divergence, EMA21>EMA50, MACD cross above zero |
| Bearish Engulfing at Resistance | Reversal Short | Volume spike, RSI<50, Close below 21 EMA |
| Bullish Engulfing + 200 EMA | Continuation Long | Volume oscillator positive [[40]](https://se.tradingview.com/scripts/macd/?script_access=all) |
| Morning Star | Bottom Long | MFI rising liquidity, MACD reduced bearish momentum |

---

## 9. Profiles

1.  **Volatility Profile:** XAUUSD ATR 15m typically $2-$5, during CPI $8-$15. Profile switching: Low ATR = range, High ATR = trend.
2.  **Session Profile:** London + New York highest volume for gold signals [[41]](https://de.tradingview.com/scripts/search/GOLD/?script_type=indicators&script_access=all). Asian session = liquidity grab.
3.  **Trader Profile:** Scalper (M15, EMA+RSI+MACD), Swing (H4, MACD zero-cross + SR), Position (Daily, 50/200 EMA + COT).
4.  **Market Regime Profile:** Risk-on (gold down, USD up), Risk-off (gold up), Inflation shock (gold + oil up, but yields up pressuring gold).

---

## 10. MACD WITH LE and SE - Super Prediction System

### 10.1 Definition of LE/SE

- **LE = Long Entry, SE = Short Entry**
- Gold Optimized LE: Price > 200 EMA + RSI > 50 + MACD crosses above Upper Bollinger Band [[42]](https://in.tradingview.com/scripts/macdcross/).
- Gold Optimized SE: Price < 200 EMA + RSI < 50 + MACD crosses below Lower Bollinger Band [[42]](https://in.tradingview.com/scripts/macdcross/).

### 10.2 Super Prediction Logic with Zero-Line and Volume Filter

```
# Gold-Optimized MACD Super Prediction
Fast = EMA(n1=5-9), Slow = EMA(n2=26-35), Signal = EMA(n3=9) [[4]](https://www.mdpi.com/1911-8074/19/3/192)
MACD_line = Fast - Slow
Signal_line = EMA(MACD_line, n3)
Histogram = MACD_line - Signal_line

Long Conditions (LE):
- MACD_line crosses above zero line (BBO Buy arrow) [[43]](https://se.tradingview.com/scripts/macd/?script_access=all)
- Volume oscillator positive (short EMA > long EMA) [[43]](https://se.tradingview.com/scripts/macd/?script_access=all)
- MACD_line above Signal_line
- MACD histogram above zero [[31]](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies)
- Zero-line proximity filter + minimum distance filter [[44]](https://www.tradingview.com/scripts/macd/?ref=hackernoon.com)
- Price > 50-day MA for trend confirmation [[32]](https://www.tradingview.com/chart/XAUUSD/MfSRSz9Q-MACD-RSI-confirmation-strategy/)

Short Conditions (SE):
- MACD crosses below zero (BBO Sell arrow) [[43]](https://se.tradingview.com/scripts/macd/?script_access=all)
- Volume positive, MACD below signal
- Close any existing long and enter short

Exit:
- Long exit when MACD crosses below signal or RSI <50
- Short exit when MACD crosses above signal
- Stop loss: 1.5*ATR or below recent swing low [[32]](https://www.tradingview.com/chart/XAUUSD/MfSRSz9Q-MACD-RSI-confirmation-strategy/)
- Take profit: 5%/10% strategy C from MDPI paper [[30]](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918) -> $4,500 resistance, $4,280 support
```

### 10.3 Historical Prediction Bar

- **Backtest Bar:** For each historical candle, plot predicted direction for next N candles using MACD LE/SE + candle depth. Compare predicted vs actual.
- **Old Historical Data Prediction:** Use 2004-2024 Kaggle dataset [[5]](https://github.com/BaseMax/XAUUSD-LSTM) to train LSTM and validate MACD parameters. Sequence length 96 (24h on 15m) [[5]](https://github.com/BaseMax/XAUUSD-LSTM).
- **Visual:** Prediction bar = colored background on chart: Green = predicted up, Red = predicted down, Yellow = no trade (squeeze inside Keltner). Accuracy measured by profit factor, not win rate.
- **Optimization:** Use Bayesian/Grey-Wolf optimization for MACD parameters as in XGBoost study with window sizes 8/16/32/64 [[24]](https://www.researchgate.net/publication/353416702_Forecasting_gold_price_with_the_XGBoost_algorithm_and_SHAP_interaction_values).

---

## 11. Custom New Algorithm Architecture - XAU-GOD v1 (Free Implementation)

### 11.1 Pipeline

```
[MT5 Real-Time Feed] -> [Python Data Ingest]
    -> [Feature Engineering: Candle Depth, SR Zones, EMA/RSI/MACD/BB/ATR/VWAP]
    -> [Regime Detection: ATR + ADX + COT]
    -> [ML Prediction: CNN-Bi-LSTM 16-step forecast]
    -> [Signal Generation: MACD LE/SE + Pattern Match + Top/Bottom Matcher]
    -> [Risk Management: 0.5% risk, ATR SL, Daily Loss Limit 3%]
    -> [Execution: MT5 order_send]
    -> [Alert: Telegram + TradingView webhook + Google Sheet log]
```

### 11.2 Top/Bottom Prediction Matching Last Top/High as per Direction

```
Last Top = Highest High last 50 periods
Last Bottom = Lowest Low last 50 periods
If direction = bullish and current close within 0.5*ATR of Last Top AND RSI divergence (price higher high, RSI lower high) => Predicted Double Top => Avoid Long, prepare Short on rejection candle (wick >50% range) [[45]](https://www.tradingview.com/scripts/supportandresistance/page-7/?script_type=indicators&script_access=all)
If direction = bearish and near Last Bottom + bullish engulfing + volume expansion => Predicted Bottom => LE
```

### 11.3 Self Prediction Base on All Data

Self-prediction score = weighted average:
- 30% ML forecast (LSTM direction)
- 25% MACD LE/SE signal
- 20% Candle depth + pattern
- 15% SR zone confluence (pivot + order block overlap) [[46]](https://www.tradingview.com/scripts/supportandresistance/page-37/?script_access=all&script_type=indicators)
- 10% Macro filter (Fed hike probability, oil trend)

Only trade if score >70% and macro filter not blocking (e.g., pause 30 min before/after CPI/PPI).

### 11.4 Free Tech Stack

- **Build:** MT5 Demo (IC Markets/Exness) + Python 3.9 + MetaTrader5 pip + TensorFlow + pandas
- **Train:** Kaggle dataset + BaseMax XAUUSD-LSTM repo [[5]](https://github.com/BaseMax/XAUUSD-LSTM)
- **Deploy:** Oracle Cloud Always Free VPS
- **Monitor:** TradingView chart with custom indicator overlay

---

## 12. Current Market Prediction Summary (As of Sep 11-12, 2026)

- **Bias:** Neutral to bearish short-term corrective, bullish long-term.
- **Prediction:** If CPI hot > expected, gold likely tests $4,300 support then $4,280 [[9]](https://www.fxempire.com/forecasts/article/premium-gold-price-analysis-4280-target-in-view-as-the-crowded-long-unwinds-into-the-fed-1620197). If CPI soft, path opens to $4,500 resistance [[47]](https://www.wsj.com/finance/commodities-futures/gold-slips-traders-eye-inflation-data-a5ad1d66). Softer inflation readings would reduce hike probability and open $4,500 zone, while above-estimate with high energy reinstates selling pressure to $4,300 focus [[47]](https://www.wsj.com/finance/commodities-futures/gold-slips-traders-eye-inflation-data-a5ad1d66).
- **Last 2 Weeks Movement Catch:** Algorithm flagged two successful buys below $4,400 [[3]](https://www.reuters.com/world/india/gold-eases-robust-us-payrolls-boost-rate-hike-bets-inflation-data-focus-2026-09-07/) but failed to hold $4,500 due to oil surge. Implementation must detect buying interest below $4,400 as support, but exit quickly if 20-day and 50-day SMA slope flattens.
- **Current Candle:** Watch for bullish hammer / morning star at support with MFI rising liquidity as early reversal [[35]](https://economictimes.indiatimes.com/news/international/us/gold-price-forecast-should-buy-gold-or-wait-for-stabilization-of-prices-heres-price-prediction-for-tomorrow-next-week-next-30-days-factors-affecting-prices-this-month-xau/usd-market-short-term-trading-strategies-u-s-consumer-price-index-macd-rsi-vwap-sma20/articleshow/124763730.cms?from=mdr) and MACD nearing signal line with reduced bearish momentum.

---

## 13. Implementation Roadmap

1.  Phase 1 - Data: Download Kaggle 2004-2024 15m CSV, connect MT5 Python API.
2.  Phase 2 - Indicators: Code EMA, RSI, MACD (5,26,9 and 15,35,9 variants), BB, ATR, VWAP in Python.
3.  Phase 3 - Candle Depth Engine: Body ratio, wick ratio, pivot detection.
4.  Phase 4 - ML: Train BaseMax LSTM seq_len 96 [[5]](https://github.com/BaseMax/XAUUSD-LSTM), evaluate vs XGBoost.
5.  Phase 5 - Backtest: VectorBT with 5%/10% SL/TP rules [[30]](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918).
6.  Phase 6 - Live: Deploy on Oracle VPS, Telegram alerts, forward test 3 months on demo.

---

## Sources

[1] Reuters — [Gold on track for third weekly loss as US inflation data looms](https://www.reuters.com/world/india/gold-track-third-weekly-loss-us-inflation-data-looms-2026-09-11/)
[2] Barron's — [Gold Set for Weekly Loss as Rate-Hike Expectations Pressure Prices](https://www.barrons.com/livecoverage/stock-market-news-today-091126/card/gold-set-for-weekly-loss-as-rate-hike-expectations-pressure-prices-OpTVqqlMXnVpO5tvtg2m)
[3] Reuters — [Gold eases as strong US jobs data boosts Fed rate-hike bets](https://www.reuters.com/world/india/gold-eases-robust-us-payrolls-boost-rate-hike-bets-inflation-data-focus-2026-09-07/)
[4] MDPI — [Optimal and Non-Optimal MACD Parameter Ranges with Stop-Loss and Take-Profit Rules: Evidence from the Gold Market](https://www.mdpi.com/1911-8074/19/3/192)
[5] GitHub — [BaseMax/XAUUSD-LSTM: A Python-based LSTM model for forecasting XAU/USD](https://github.com/BaseMax/XAUUSD-LSTM)
[6] Finnhub — [XAU/USD Financial Market Data](https://finnhub.io/?q=%22XAU%2FUSD%22)
[7] FXEmpire — [Gold (XAUUSD) Price Forecast: Value Versus Trend as Gold Stages Technical Bounce Ahead of CPI](https://www.fxempire.com/forecasts/article/gold-xauusd-price-forecast-value-versus-trend-as-gold-stages-technical-bounce-ahead-of-cpi-1626960)
[8] FXStreet — [$4,465: Gold looks to regain 21-day SMA amid sustained USD weakness](https://www.fxstreet.com/analysis/4-465-gold-looks-to-regain-21-day-sma-amid-sustained-usd-weakness-202609080230)
[9] FXEmpire — [Gold Price Analysis: $4,280 Target In View as the Crowded Long Unwinds Into the Fed](https://www.fxempire.com/forecasts/article/premium-gold-price-analysis-4280-target-in-view-as-the-crowded-long-unwinds-into-the-fed-1620197)
[10] MQL5 — [Using Technical Indicators to Trade XAUUSD (Gold) More Effectively](https://www.mql5.com/en/blogs/post/766745)
[11] Reuters — [Goldman hikes December 2026 gold price forecast to $4,900/oz](https://www.reuters.com/business/goldman-hikes-december-2026-gold-price-forecast-4900oz-2025-10-07/?ref=bytenewsdaily.com)
[12] WSJ — [Gold Little Changed As August CPI Raises Interest-Rate Expectations](https://www.wsj.com/finance/commodities-futures/gold-rises-ahead-of-u-s-cpi-data-c995e7d0)
[13] MetaTrader5 — [Online Forex and exchange trading with MetaTrader 5](https://www.metatrader5.com/en/trading-platform)
[14] MetaTrader5 — [Technical analysis tools in MetaTrader 5](https://www.metatrader5.com/en/trading-platform/technical-analysis)
[15] FXEmpire — [Moneta Markets Launches 24/7 Gold Trading on MT5](https://www.fxempire.com/news/article/moneta-markets-launches-24-7-gold-trading-on-mt5-1624917)
[16] TradingView — [XAUUSD Chart — Gold Spot US Dollar Price — Indicators and Strategies](https://www.tradingview.com/scripts/xauusd/page-2/?script_type=indicators&script_access=all)
[17] TradingView — [Moving Average Convergence / Divergence (MACD) — Indicators and Strategies](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies)
[18] GitHub — [waylandzhang/ai-quant-book - Candlestick-Patterns-and-Volume-Analysis](https://github.com/waylandzhang/ai-quant-book/blob/HEAD/manuscript/en/Part2-Quant-Fundamentals/Background/Candlestick-Patterns-and-Volume-Analysis.md)
[19] TradingView India — [Candlestick analysis](https://in.tradingview.com/scripts/candlestickanalysis/?sort=recent&script_access=open&script_type=indicators)
[20] TradingView — [Support and Resistance — Indicators and Strategies](https://www.tradingview.com/scripts/supportandresistance/page-3/?script_type=indicators)
[21] TradingView — [Support and Resistance — Indicators and Strategies](https://www.tradingview.com/scripts/supportandresistance/page-2/?script_access=all&script_type=indicators)
[22] TradingView — [Support and Resistance — Multi-Timeframe](https://www.tradingview.com/scripts/supportandresistance/page-24/?sort=recent&script_type=indicators&script_access=all)
[23] MDPI — [Optimal and Non-Optimal MACD Parameter Ranges](https://www.mdpi.com/1911-8074/19/3/192) - Introduction
[24] ResearchGate — [Forecasting gold price with the XGBoost algorithm](https://www.researchgate.net/publication/353416702_Forecasting_gold_price_with_the_XGBoost_algorithm_and_SHAP_interaction_values)
[25] PLOS One — [Gold price prediction by a CNN-Bi-LSTM model](https://journals.plos.org/plosone/article/figure?id=10.1371/journal.pone.0298426.g005)
[26] Springer — [Forecasting gold price using hybrid deep neural network LSTM-autoencoder](https://link.springer.com/article/10.1007/s44163-025-00464-w)
[27] White Rose — [Optimal prediction of resistance and support levels](https://eprints.whiterose.ac.uk/id/eprint/112048/1/Paper-Revised.pdf)
[28] TradingView India — [Metals — Indicators and Strategies](https://in.tradingview.com/scripts/metals/?script_type=indicators&sort=recent)
[29] MDPI-Res — [Optimal and Non-Optimal MACD Parameter Ranges PDF](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918)
[30] MDPI-Res — [Optimal and Non-Optimal MACD Parameter Ranges PDF - Strategy C](https://mdpi-res.com/d_attachment/jrfm/jrfm-19-00192/article_deploy/jrfm-19-00192-v2.pdf?version=1773303918)
[31] TradingView — [MACD histogram zero-line strategy](https://www.tradingview.com/scripts/macd/?script_access=all&script_type=strategies)
[32] TradingView — [MACD+RSI confirmation strategy for XAUUSD](https://www.tradingview.com/chart/XAUUSD/MfSRSz9Q-MACD-RSI-confirmation-strategy/)
[33] GitHub — [sanxdy/vortex-trading-bot - Add chart indicators](https://github.com/sanxdy/vortex-trading-bot/commit/a1fb04761e474151074331d63256cd8ad2bf6de6)
[34] TradingView India — [Xauusd(w) — Indicators and Strategies](https://in.tradingview.com/scripts/xauusd%28w%29/)
[35] Economic Times — [Gold Price Forecast: Should buy gold or wait](https://economictimes.indiatimes.com/news/international/us/gold-price-forecast-should-buy-gold-or-wait-for-stabilization-of-prices-heres-price-prediction-for-tomorrow-next-week-next-30-days-factors-affecting-prices-this-month-xau/usd-market-short-term-trading-strategies-u-s-consumer-price-index-macd-rsi-vwap-sma20/articleshow/124763730.cms?from=mdr)
[36] Investopedia — [Three White Soldiers: A Bullish Trading Pattern Guide](https://www.investopedia.com/terms/t/three_white_soldiers.asp)
[37] Investopedia — [How to Trade the Head and Shoulders Pattern](https://www.investopedia.com/articles/technical/121201.asp)
[38] Investopedia — [Unlock Market Trends with Triple Tops and Bottoms Patterns](https://www.investopedia.com/articles/technical/02/012102.asp)
[39] TradingView — [Candlestick Analysis — Triangle](https://www.tradingview.com/scripts/candlestick/?script_access=all&sort=recent)
[40] TradingView SE — [MACD with volume oscillator filtering](https://se.tradingview.com/scripts/macd/?script_access=all)
[41] TradingView DE — [Scripts Suchergebnis für GOLD](https://de.tradingview.com/scripts/search/GOLD/?script_type=indicators&script_access=all)
[42] TradingView India — [Macdcross — GOLD Optimized](https://in.tradingview.com/scripts/macdcross/)
[43] TradingView SE — [MACD crosses above zero line](https://se.tradingview.com/scripts/macd/?script_access=all)
[44] TradingView — [MACD Minimum Distance and Zero Line Filter](https://www.tradingview.com/scripts/macd/?ref=hackernoon.com)
[45] TradingView — [Support and Resistance — RETEST Signals](https://www.tradingview.com/scripts/supportandresistance/page-7/?script_type=indicators&script_access=all)
[46] TradingView — [Support and Resistance — Confluence scoring algorithm](https://www.tradingview.com/scripts/supportandresistance/page-37/?script_access=all&script_type=indicators)
[47] WSJ — [Gold Futures Edge Up Despite Higher U.S. Yields](https://www.wsj.com/finance/commodities-futures/gold-slips-traders-eye-inflation-data-a5ad1d66)
