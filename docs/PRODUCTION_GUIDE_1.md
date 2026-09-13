# Production Guide - Real Demo + Real Account

## Demo Account Setup (SAFE - Start Here)

### Step 1: MT5 Demo
1. Download MT5 from https://www.metatrader5.com/ or broker (Exness, IC Markets)
2. Install, open, File -> Open Account -> Demo
3. Choose leverage 500, deposit $10,000
4. Note Login, Password, Server (e.g., Exness-MT5Trial8 or MetaQuotes-Demo)
5. Enable Algo Trading: Toolbar green play button -> must be green

### Step 2: Python Environment
```bat
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac (mock mode for dev)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configuration .env.demo
```
MT5_LOGIN=your_demo_login
MT5_PASSWORD=your_demo_password
MT5_SERVER=Exness-MT5Trial8
SYMBOLS=XAUUSD,BTCUSD
TIMEFRAMES=M15,H1,H4,D1
RISK_PER_TRADE=0.005
MAX_DAILY_LOSS=0.03
LIVE_TRADING=false
AUTO_TRADING=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Step 4: Run Backend
```bat
python main.py
# Output: MT5 Connected: Exness-MT5Trial8 - 12345678
# Backend http://localhost:8000
# Docs http://localhost:8000/docs
```

### Step 5: Frontend Dashboard
- Double-click frontend/dashboard.html
- Dashboard shows MOCK-DEMO CONNECTED (green)
- If backend running on Windows, it auto-connects and shows REAL-DEMO
- Multi-timeframe viewer 2x2 grid, realtime signals every 3s
- Scan Markets button -> triggers alerts

## Real Account Setup (PRODUCTION - WARNING)

### ⚠️ Prerequisites - MUST Complete Before Real:
- [ ] 2-3 months demo forward test with profit factor >1.2
- [ ] Win rate >55% on demo
- [ ] Max drawdown <10%
- [ ] 100+ trades on demo
- [ ] Telegram alerts working
- [ ] Risk manager tested (daily loss limit blocks)
- [ ] You understand ATR SL/TP logic

### Real Account Configuration .env.real

```
MT5_LOGIN=your_real_login
MT5_PASSWORD=your_real_password
MT5_SERVER=Exness-Real or ICMarkets-Real
SYMBOLS=XAUUSD
TIMEFRAMES=M15,H1,H4,D1
RISK_PER_TRADE=0.002  # Lower for real start
MAX_DAILY_LOSS=0.02   # Stricter for real
LIVE_TRADING=true
AUTO_TRADING=false    # Start false, manual confirmation first 10 trades
CONFIRM_REAL_TRADE=true
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Real Trading Safety Features

1. **CONFIRM_REAL_TRADE=true:** First 10 real trades require typing YES in console
2. **Risk Manager:** Blocks if daily loss >2-3%, logs to file
3. **Volume Limit:** Real starts with 0.01 lot max for first week
4. **Telegram:** Every real order sends Telegram with ticket, price, SL/TP
5. **Equity Guard:** If equity drops 5% from start, auto-disables auto trading

### Production Deployment Options

**Option 1: Local Windows (Recommended for MT5)**
- Windows 10/11 with MT5 installed
- Run backend as service: `python main.py` in startup
- Frontend dashboard always open on second monitor

**Option 2: VPS (Oracle Free / Contabo)**
- Windows VPS required for real MT5 (Linux cannot run MT5 real)
- Install MT5 on VPS, setup backend as Windows service
- Use Ngrok or Cloudflare Tunnel to expose dashboard

**Option 3: Hybrid**
- Backend on Windows local/VPS with MT5
- Frontend hosted on Vercel/Netlify, connects via WebSocket

### Monitoring in Production

- **Dashboard:** Keep open 24/5, check positions, equity curve, drawdown
- **Telegram:** Alerts for LE/SE ≥70, plus every real execution
- **Log File:** backend/logs/trading.log rotates daily
- **MT5 Terminal:** Keep MT5 open, check Experts tab for errors

### Troubleshooting

- `MT5 initialize failed`: MT5 not installed or path wrong in .env MT5_PATH
- `Login failed`: Wrong login/password/server
- `No data`: Symbol name mismatch (some brokers use GOLD, BTCUSD, BTCUSD.a)
- `Order send failed 10016`: Invalid SL/TP (too close), increase ATR multiplier
- `WebSocket disconnected`: Backend not running or port blocked

### Backup & Recovery

- Backup .env files securely (encrypted)
- Backup historical_data CSVs weekly
- Backup logs
- MT5 demo account expires in 30 days - create new demo and update .env

### Legal Disclaimer

This bot is educational, not financial advice. Trading forex/crypto involves substantial risk of loss. Past backtest 25% return (Gate Research) or 73% accuracy (Attention-LSTM) does not guarantee future. Always start demo. Never risk more than you can afford to lose. Author not responsible for losses.
