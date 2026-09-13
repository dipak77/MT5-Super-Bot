# MT5 SUPER BOT V2 - PROD GRACE - ACTION ENGINE EDITION
## Master Agent Review + All Subagents Knowledge Integrated

This is V2 - Top Level Upgrade with all bugs fixed and missing features added.

### 🔥 What was Fixed (Code Reviewer + Tester)

**Critical Bugs Fixed:**
1. `super_algo.py` RSI - Now Wilder smoothing (was SMA), handles inf
2. `candle_depth` KeyError - Now always returns upper_wick, lower_wick, wick_imbalance, uses range not body for hammer detection
3. `detect_sr_zones` naive nlargest(3) - Now pivot left=3 right=3, rejection count, order block & breaker polarity flip, confluence scoring, fresh/broken states
4. Scoring overflow SE max 105 -> clamped 0-100
5. `main.py` deprecated `@app.on_event("startup")` -> lifespan
6. `main.py` /api/execute bypassed risk - Now goes through RiskManagerV2 + ActionEngine
7. Sync blocking get_candles -> async to_thread
8. ConnectionManager leak -> fixed disconnect
9. CORS ["*"] open -> whitelist + origin regex
10. Dashboard undefined .h error -> null checks, try-catch, initial data pre-fill
11. NaN handling only float -> now handles inf, -inf, NaN, ISO time

### 🚀 Top Level Features Added (Planner + Depth + Auto Bot Agents)

#### 1. Action Engine (action_engine.py) - NEW CORE
- Depth analysis before every trade:
  - Candle Depth (body ratio, wick imbalance, volume confirm)
  - Trade Movement/Direction (strong_bullish, weak, bearish)
  - Past Movement Base Analysis (compare current to last 50 failed breakouts)
  - Historical Closed Top/High Resistant Base Analysis (dist in ATR adaptive per symbol, rejection count, double top with RSI divergence, breaker)
  - MTF Alignment (M15/H1/H4/D1 trend alignment score 0-20)
  - Strategies Review (Trend Pullback, Mean Reversion 25% Gate, Breakout)
  - Pattern Analysis (hammer, engulfing, tweezer, head & shoulders)
- Overall score 0-100 with weights: 25% MTF, 20% MACD LE/SE, 15% Candle Depth, 15% Pattern, 10% SR/Top/Bottom, 10% Strategies, 5% Volume/On-Chain
- Can trade logic: blocks if score<60, double top risk, doji indecision, repeating failed pattern

#### 2. Approval vs Auto-Approved Flow
- **Approval Mode:** Score >=60 but < threshold -> pending queue, requires user approval via dashboard Approve button or Telegram /approve
- **Auto-Approved Demo:** Score >=70 + depth pass -> auto executes (if AUTO toggle on)
- **Auto-Approved Real Strict:** Score >=85 + all depth pass + risk ok + beyond first 10 trades -> auto executes, else approval
- **Real First 10 Trades:** Always require approval even if score >=85 (safety)
- **Pending Queue:** dashboard shows pending actions with depth analysis view, Approve/Reject buttons, Approve All
- **Telegram:** /approve <id> and /reject, alerts for pending

#### 3. MTF Alignment Check (super_algo.py)
- Checks bullish_count / bearish_count across 4 TFs
- 3+ aligned = 20 score strong alignment, 2 = 10 weak, else 0
- Detail: "Strong bullish alignment 3/4 TFs LE"

#### 4. Past Trade Movement Base Analysis
- Compares current price to recent 50 highs within 0.15% XAU / 0.2% BTC
- If near recent failed high -> pastScore -10 caution, else +10 clear

#### 5. Historical Closed Top/High Resistant Base Analysis (Enhanced)
- Adaptive ATR distance: XAU 0.5 ATR = $2-5, BTC 0.5 ATR = $150-300, threshold 0.8 ATR = close
- Rejection count: counts how many times price rejected at level in last 100 bars
- Order Block polarity flip: close beyond zone flips former support to resistance (breaker)
- Double top/bottom detection with RSI divergence: price higher high + RSI lower high
- Strongest resistance/support with rejection count

#### 6. Risk Manager V2
- Daily PnL tracking, reset new day
- Equity guard -5% from peak auto-disables auto trading
- Risk per trade check: |price-sl|*volume*contract (100 XAU, 1 BTC) vs max risk
- Real confirmation first 10 trades
- Volume limit real start 0.01 max first week (enforced in ActionEngine)
- Log rotation, equity.json state save

#### 7. Main FastAPI Service (main.py)
- Lifespan architecture, async get_candles, clean CORS whitelist, zero memory leaks, risk checks on all execute/scan/ws
- Endpoints: /api/status, /api/account, /api/account/reconnect, /api/risk, /api/actions/pending, /api/actions/history, /api/actions/{id}/approve, /api/actions/{id}/reject
- Scan creates actions with multi-dimensional depth analysis, auto executes auto_approved if risk checks pass
- WebSocket broadcasts real-time prices, account sync, pending_actions, and risk metrics
- Integrated automated MT5 desktop terminal discovery & background keepalive auto-reconnect loop

#### 8. Professional Trading Dashboard (dashboard.html)
- Institutional TradingView workstation with multiple technical overlays (EMA ribbons, SuperTrend, Bollinger Bands, RSI, MACD, Volume)
- Quick One-Click Order Execution Bar directly atop chart (Instant Buy/Sell with pre-calculated lot sizing, SL, TP)
- Reconnect MT5 desktop IPC link button with real-time status diagnostics
- Action Engine Pending Queue with live depth analysis audit, Approve / Reject controls, and Auto-Bot toggles

### 📊 System Architecture & Verification

- **Data Fetcher**: Hybrid live MT5 terminal polling with seamless fallback to Yahoo Finance / historical CSVs
- **Signal Engine**: 5-strategy confluence (Trend Pullback, Mean Reversion, Breakout, Pattern Recognition, Multi-Timeframe Matrix)
- **Risk Management**: Enforces strict daily drawdown limits (-3%), max position limits, and automatic circuit breakers
- **Terminal IPC**: Auto-discovers local 64-bit desktop terminal (`terminal64.exe`) across standard installation paths and keeps connection alive

### 🔧 How to Run

**Option 1: Windows One-Click Batch File (Recommended)**
```bat
run_local.bat
```

**Option 2: Manual CLI Startup**
```bat
cd backend
pip install -r requirements.txt
python main.py
```
Open browser to:
- **Trading Dashboard**: `http://localhost:8000/dashboard`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 📦 Clean Repository Structure (Single Canonical Files Only)

- `backend/`
  - `main.py` — FastAPI application & WebSocket server
  - `super_algo.py` — 5-strategy signal engine & multi-timeframe analysis
  - `risk_manager.py` — Dynamic position sizing & risk protection
  - `mt5_trader.py` — Native MetaTrader 5 IPC integration & terminal discovery
  - `action_engine.py` — Trade quality scoring & depth evaluation
  - `alert_manager.py` — Telegram & console notification dispatcher
  - `config.py` — Environment configuration loader
  - `data_fetcher.py` — Multi-source market data provider
  - `requirements.txt` — Python dependencies
- `frontend/`
  - `dashboard.html` — Full-featured TradingView Pro trading workstation
- `docs/` — Canonical technical architecture & indicator documentation
- `run_local.bat` — One-click launcher

