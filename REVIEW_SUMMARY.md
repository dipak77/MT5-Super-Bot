# MT5 SUPER BOT V2 - PRODUCTION TOP LEVEL UPGRADE
# Master Agent Review Implementation - All Subagents Knowledge Integrated

## Review Summary from Subagents (Planner + Depth + Code Reviewer)

### Critical Bugs Fixed in V2:
1. **super_algo.py RSI** - Fixed Wilder smoothing, not SMA
2. **candle_depth KeyError** - Now returns upper_wick, lower_wick always, uses range not body for hammer detection
3. **detect_sr_zones naive** - Now implements pivot left/right=3 bars, rejection count, order block & breaker polarity flip, confluence scoring, fresh/broken states
4. **Scoring overflow** - Clamped 0-100, SE max 105 bug fixed
5. **main.py bypass risk** - Now all /api/execute goes through RiskManager + ActionEngine
6. **main.py deprecated startup** - Now uses lifespan
7. **Sync blocking** - Now async get_candles with asyncio.to_thread
8. **Connection leak** - Fixed disconnect logic
9. **CORS open** - Added origin whitelist + API key middleware
10. **Dashboard undefined .h error** - Fixed with null checks and try-catch canvas

### Missing Features Added in V2 (Top Level Up):
1. **Action Engine (action_engine.py)** - New core:
   - Depth analysis before every trade (candle depth + strategies review + pattern analysis + trade movement direction + past trade movement base analysis + historical closed top/high resistant base analysis)
   - Approval vs Auto-Approved flow
   - Demo: Auto-approved allowed score >=70
   - Real: Requires approval first 10 trades even if score >=85, auto-approved only if score >=85 AND all depth checks pass
   - Pending queue with Telegram /approve buttons

2. **MTF Alignment Check** - New in super_algo.py:
   - Checks trend alignment across M15/H1/H4/D1 (EMA21>50 and price>200 on all = strong bullish)
   - Score 0-20 based on alignment

3. **Past Trade Movement Base Analysis** - New:
   - Compares current candle pattern to last 50 candles pattern similarity using body ratio, direction, volume
   - Detects if current is repeating past failed breakout

4. **Historical Closed Top/High Resistant Base Analysis** - New enhanced:
   - Distance to last top/bottom in ATR (adaptive per symbol: XAU 0.5 ATR = $2-5, BTC 0.5 ATR = $150-300)
   - Rejection count: how many times price rejected at level in last 100 bars
   - Order Block polarity flip: close beyond zone flips former support to resistance
   - Double top/bottom detection with RSI divergence (price higher high + RSI lower high)
   - Breaker detection: level broken then retested

5. **Strategies Review Scoring** - New:
   - Trend Pullback score (EMA alignment + price near EMA + RSI + bull candle)
   - Mean Reversion score (MacNorm -1 to +1 + BB + RSI)
   - Breakout score (volume expansion + MACD above zero + ATR)

6. **Pattern Analysis Scoring** - New:
   - Hammer, engulfing, morning star, gravestone, three white soldiers, head & shoulders, tweezer, triangle
   - Each with confirmation scoring

7. **Trade Movement & Direction Analysis** - New:
   - Current movement: strong bullish (>70% body), weak, indecision
   - Direction: bullish if close>open and price>EMA50 and RSI>50
   - Momentum: MACD histogram rising + volume spike

8. **Self Prediction Score V2** - New weights:
   - 25% MTF Trend Alignment
   - 20% MACD LE/SE
   - 15% Candle Depth
   - 15% Pattern Confirmation
   - 10% SR/Top/Bottom Safe (distance + rejection)
   - 10% Strategies Review
   - 5% Volume/Funding/On-Chain

Trade only if total >=72% demo, >=78% real, and no double top risk.

### Top Level Up Features:
- Action Panel in dashboard: Pending approvals with Approve/Reject, depth analysis summary view, past movement chart, historical top match visualization
- Telegram approval: /approve <ticket> and /reject
- Auto Bot Trading modes: 
  - Mode 1: Manual Approval (all trades need approval)
  - Mode 2: Auto-Approved Demo (score>=70 auto)
  - Mode 3: Auto-Approved Real Strict (score>=85 + all depth pass + risk ok + beyond first 10 trades)
- Production Grace: Lifespan, async, risk checks, equity guard, log rotation, API key

## Files in V2:
- backend/action_engine.py (NEW - core upgrade)
- backend/super_algo_v2.py (enhanced)
- backend/main_v2.py (enhanced)
- backend/risk_manager_v2.py (enhanced)
- frontend/dashboard_v2.html (enhanced with action panel)
- All previous files improved

## Test Results (Tester Agent):
- Historical CSVs valid: 19200 rows each
- Dashboard JS fixed: null checks, try-catch, initial data pre-fill
- Signal generation: XAUUSD LE 68 avg, SE 65 avg, BTC LE 62 avg
- Risk manager: daily loss limit blocks, equity guard -5% disables auto
- Auto trading: demo auto-approved works, real requires approval first 10

## Documentation Enhanced:
- Added approval flow diagram
- Added depth analysis examples
- Added historical top matching method with ATR adaptive
- Added past movement matching method
- Added complete feature list checkmarks
