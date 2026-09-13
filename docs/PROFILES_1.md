# Profiles Documentation

## 1. Volatility Profile

### XAUUSD
- ATR 15m typically $2-$5 normal, $8-$15 during CPI/PPI
- Gold volatile, ATR helps adapt: dynamic SL, adjust TP, avoid low-vol
- BTC higher volatility than ETH, reflecting downtrend consolidation, stabilization, rapid rebound
- Profile switching: Low ATR = range market, High ATR = trend market
- Volatility measured via standard deviation of daily returns

### BTCUSD
- BTC exhibited greater volatility than ETH over past 2 weeks
- Funding rate volatility more pronounced than ETH, frequently negative = short dominance bearish bias
- Liquidation cascade risk: average daily liquidation $732M Feb 24-Mar 3, longs $542M/day vs shorts $190M/day = leveraged longs higher risk

## 2. Session Profile

- **Gold:** London + New York highest volume for gold signals, Asian session = liquidity grab
- **BTC:** Crypto 24/7 but US session + FOMC days high liquidation risk
- **Best Times:** 
  - XAUUSD: 13:00-17:00 GMT (London-NY overlap)
  - BTCUSD: 13:00-21:00 GMT + FOMC announcement windows

## 3. On-Chain Profile (BTC)

- **Heavy Supply Resistance:** $77,100-$80,200 where long-term holders sold 539,000 BTC over 30 days = nearest and heaviest resistance above current price
- **Technical Levels:** 365-day MA $81,700 bull confirmation (bull markets historically begin when close above), 200-day MA $70,000 key support
- **SOPR Signal:** Uses Glassnode SOPR on-chain data to identify cheap/expensive channel
- **Supply Weighted MA:** Marks support/resistance, uptrend slope halves after each halving, slope correlated with new supply rate
- **ETF Flows:** $1.01B inflows in 3 days, $730.8M on Sep 3 = institutional support
- **Open Interest:** BTC futures OI sharply declined below $51B = deleveraging, cautious sentiment. Rebound but below Feb peak = conservative inflows
- **Funding Rates:** Negative funding = short dominance, deleveraging phase, strengthening bearish sentiment short-term

## 4. Trader Profiles

- **Scalper:** M15, EMA+RSI+MACD 15-35-9, Stoch, BB, VWAP. Tighter TP/SL & faster entries for active intraday. BTCUSDT Futures 1m needs quick execution, monitor slippage/latency.
- **Swing:** H4, MACD zero-cross + SR zones, 50/200 EMA, ATR SL. Holds days.
- **Position:** Daily, 50/200 EMA + COT report + central bank buying + ETF inflows. Long-term bullish constructive.
- **DCA:** Bitcoin DCA enhanced by MACD + Fear & Greed Index signals, Backtrader framework.

## 5. Market Regime Profile

- **Risk-on:** Gold down, USD up, BTC up with Nasdaq, yields up pressure gold
- **Risk-off:** Gold up safe-haven, BTC down risk asset, USD up
- **Inflation Shock:** Gold + oil up together, but yields up pressuring gold (trade barriers + geopolitical disruption support bullion but if push inflation higher, tighter policy lifts yields and increases opportunity cost)
- **Deleveraging:** Declining open interest + rising long liquidations + funding negative = caution, liquidity tightening

## 6. Sentiment Profile

- **LSR (Long/Short Taker Ratio):** BTC LSR 0.90-1.10 balanced, ETH 0.85-1.05 more volatile. Inverse correlation with price = buy dip cautious rebound. BTC resilience but underlying support intact, ETH underperform cautious.
- **Fear & Greed:** Used with MACD for DCA enhancement
- **ETF Inflows vs Yields:** Continued ETF inflows + stablecoin growth support, Fed outlook + elevated Treasury yields constraints
