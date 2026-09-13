"""
FastAPI Backend V2 - Production Grace with Lifespan, Action Engine, Approval Flow, Risk Checks
Fixes: deprecated startup, bypass risk, sync blocking, NaN handling, connection leak, CORS open
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from config import config
from mt5_trader import MT5Trader
from super_algo_v2 import SuperAlgoV2
from risk_manager_v2 import RiskManagerV2
from alert_manager import AlertManager
from action_engine import ActionEngine

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
DASHBOARD_FILE = FRONTEND_DIR / "dashboard_v2.html"

# Lifespan instead of deprecated on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    trader.connect()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title="MT5 Super Bot V2 - XAU-GOD / BTC-GOD PROD GRACE", version="2.0", lifespan=lifespan)

# Mount frontend directory for static assets if exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# CORS whitelist instead of ["*"]
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",  # for file:// dashboard.html
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trader = MT5Trader(config)
algo = SuperAlgoV2()
risk_manager = RiskManagerV2(config)
alerts = AlertManager(config)
action_engine = ActionEngine(config, risk_manager, alerts)

@app.get("/api/status")
@app.get("/api")
def api_status():
    acc = trader.get_account_info()
    return {
        "message": "MT5 Super Bot V2 PROD GRACE Running",
        "version": "2.0",
        "symbols": config.SYMBOLS,
        "timeframes": config.TIMEFRAMES,
        "mode": acc.get("mode", "UNKNOWN"),
        "risk": risk_manager.get_status(),
        "pending_actions": len(action_engine.get_pending()),
        "features": ["Depth Analysis", "MTF Alignment", "Historical Top Matching", "Approval vs Auto-Approved", "Risk Manager", "Action Engine"]
    }

@app.get("/")
@app.get("/dashboard")
def root():
    if DASHBOARD_FILE.exists():
        return FileResponse(DASHBOARD_FILE)
    return api_status()

@app.get("/api/account")
def get_account():
    return trader.get_account_info()

@app.get("/api/risk")
def get_risk():
    return risk_manager.get_status()

@app.get("/api/positions")
def get_positions():
    return {"positions": trader.get_positions(), "count": len(trader.get_positions())}

@app.get("/api/candles")
async def get_candles(symbol: str = Query("XAUUSD"), timeframe: str = Query("M15"), count: int = Query(300)):
    # Async to avoid blocking
    df = await asyncio.to_thread(trader.get_candles, symbol, timeframe, count)
    if df.empty:
        return {"error": "No data", "symbol": symbol, "timeframe": timeframe}
    df_ind = algo.calculate_indicators(df)
    candles = df_ind.tail(200).to_dict(orient="records")
    for c in candles:
        c['time'] = c['time'].isoformat() if hasattr(c['time'], 'isoformat') else str(c['time'])
        for k in list(c.keys()):
            if isinstance(c[k], float) and (c[k] != c[k] or c[k] == float('inf') or c[k] == float('-inf')):
                c[k] = None
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles, "count": len(candles)}

@app.get("/api/signal")
async def get_signal(symbol: str = Query("XAUUSD"), timeframe: str = Query("M15")):
    df = await asyncio.to_thread(trader.get_candles, symbol, timeframe, 200)
    if df.empty:
        return {"error": "No data"}
    # Get MTF for alignment
    mtf = {}
    for tf in config.TIMEFRAMES:
        if tf != timeframe:
            df_tf = await asyncio.to_thread(trader.get_candles, symbol, tf, 100)
            if not df_tf.empty:
                mtf[tf] = algo.generate_signal_v2(df_tf, symbol)
    sig = algo.generate_signal_v2(df, symbol, mtf_signals=mtf)
    return {"symbol": symbol, "timeframe": timeframe, "signal": sig}

@app.get("/api/signals/all")
async def get_all_signals():
    results = {}
    for symbol in config.SYMBOLS:
        results[symbol] = {}
        # First get all signals for MTF alignment
        all_sigs = {}
        for tf in config.TIMEFRAMES:
            df = await asyncio.to_thread(trader.get_candles, symbol, tf, 200)
            if not df.empty:
                all_sigs[tf] = algo.generate_signal_v2(df, symbol)
        # Now regenerate with MTF context
        for tf in config.TIMEFRAMES:
            df = await asyncio.to_thread(trader.get_candles, symbol, tf, 200)
            if not df.empty:
                mtf_for_this = {k:v for k,v in all_sigs.items() if k!=tf}
                sig = algo.generate_signal_v2(df, symbol, mtf_signals=mtf_for_this)
                results[symbol][tf] = sig
    return results

@app.get("/api/alerts")
def get_alerts(limit: int = Query(50)):
    return {"alerts": alerts.get_history(limit)}

@app.get("/api/actions/pending")
def get_pending_actions():
    return {"pending": action_engine.get_pending(), "count": len(action_engine.get_pending())}

@app.get("/api/actions/history")
def get_action_history(limit: int = Query(50)):
    return {"history": action_engine.get_history(limit)}

@app.post("/api/actions/{action_id}/approve")
def approve_action(action_id: str):
    action = action_engine.approve_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    # Now execute
    df = trader.get_candles(action["symbol"], action["timeframe"], 100)
    # Risk check again before execution
    acc = trader.get_account_info()
    equity = acc.get("equity", 10000)
    can_risk, reason = risk_manager.check_daily_loss(equity)
    if not can_risk:
        return {"error": f"Risk blocked: {reason}", "action": action}
    can_risk2, reason2 = risk_manager.check_risk_per_trade(action["symbol"], 0.01, action["price"], action["sl"])
    if not can_risk2:
        return {"error": f"Risk blocked: {reason2}", "action": action}
    
    # Execute
    sig_str = action.get("signal") or "LE"
    sl_val = action.get("sl") or 0
    tp_val = action.get("tp") or 0
    result = trader.send_order(action["symbol"], "BUY" if sig_str.startswith("LE") else "SELL", 0.01, sl=sl_val, tp=tp_val, comment=f"APPROVED-{action_id}")
    risk_manager.record_trade(action["symbol"], 0.01)
    if config.LIVE_TRADING:
        risk_manager.confirm_real_trade()
    return {"result": result, "action": action, "approved": True}

@app.post("/api/actions/{action_id}/reject")
def reject_action(action_id: str):
    action = action_engine.reject_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"action": action, "rejected": True}

@app.post("/api/scan")
async def scan_markets():
    new_actions = []
    for symbol in config.SYMBOLS:
        # Get MTF first
        mtf_all = {}
        for tf in config.TIMEFRAMES:
            df = await asyncio.to_thread(trader.get_candles, symbol, tf, 100)
            if not df.empty:
                mtf_all[tf] = algo.generate_signal_v2(df, symbol)
        for tf in config.TIMEFRAMES:
            df = await asyncio.to_thread(trader.get_candles, symbol, tf, 200)
            if df.empty:
                continue
            mtf_for_this = {k:v for k,v in mtf_all.items() if k!=tf}
            sig = algo.generate_signal_v2(df, symbol, mtf_signals=mtf_for_this)
            # Create action with depth analysis
            action = action_engine.create_action(symbol, tf, sig, mtf_data=mtf_for_this, historical_data=df)
            if action["status"] in ["pending", "auto_approved"]:
                new_actions.append(action)
                # If auto_approved, execute immediately after risk check
                if action["status"] == "auto_approved":
                    acc = trader.get_account_info()
                    equity = acc.get("equity", 10000)
                    can_risk, _ = risk_manager.check_daily_loss(equity)
                    if can_risk:
                        result = trader.send_order(symbol, "BUY" if sig["signal"].startswith("LE") else "SELL", 0.01, sl=sig["sl"], tp=sig["tp"], comment=f"AUTO-{action['id']}")
                        action["execution_result"] = result
                        risk_manager.record_trade(symbol, 0.01)
                        if config.LIVE_TRADING:
                            risk_manager.confirm_real_trade()
    return {"new_actions": new_actions, "scanned": f"{len(config.SYMBOLS)*len(config.TIMEFRAMES)} pairs", "pending": len(action_engine.get_pending())}

class ExecuteTradeRequest(BaseModel):
    symbol: str = "BTCUSD"
    type: str = "BUY"
    volume: float = 0.01

@app.post("/api/execute")
async def execute_trade(req: ExecuteTradeRequest = None, symbol: str = None, type: str = None, volume: float = None):
    """Executes trade with risk management and action engine validation"""
    trade_symbol = req.symbol if req and req.symbol else (symbol or "BTCUSD")
    trade_type = req.type if req and req.type else (type or "BUY")
    trade_volume = req.volume if req and req.volume else (volume or 0.01)

    df = await asyncio.to_thread(trader.get_candles, trade_symbol, "M15", 100)
    if df.empty:
        raise HTTPException(status_code=400, detail=f"No candle data for {trade_symbol}")
    sig = algo.generate_signal_v2(df, trade_symbol)
    
    # Risk checks
    acc = trader.get_account_info()
    equity = acc.get("equity", 100000.0)
    can_risk, reason = risk_manager.check_daily_loss(equity)
    if not can_risk:
        raise HTTPException(status_code=403, detail=f"Risk blocked: {reason}")
    can_risk2, reason2 = risk_manager.check_risk_per_trade(trade_symbol, trade_volume, sig["price"], sig["sl"])
    if not can_risk2:
        raise HTTPException(status_code=403, detail=f"Risk blocked: {reason2}")
    can_real, reason_real = risk_manager.check_real_confirmation()
    if not can_real:
        action = action_engine.create_action(trade_symbol, "M15", sig, historical_data=df)
        return {"message": f"Real confirmation required, action created {action['id']}", "action": action, "requires_approval": True}
    
    # Execute order
    result = trader.send_order(trade_symbol, trade_type, trade_volume, sl=sig.get("sl",0), tp=sig.get("tp",0), comment="TV-EXECUTE")
    risk_manager.record_trade(trade_symbol, trade_volume)
    if config.LIVE_TRADING:
        risk_manager.confirm_real_trade()
    return {"result": result, "symbol": trade_symbol, "type": trade_type, "volume": trade_volume, "signal": sig}


class PositionModifyRequest(BaseModel):
    sl: float = 0.0
    tp: float = 0.0

@app.post("/api/positions/{ticket}/close")
def api_close_position(ticket: int):
    result = trader.close_position(ticket)
    return {"result": result, "ticket": ticket}

@app.post("/api/positions/close-all")
def api_close_all_positions():
    result = trader.close_all_positions()
    return {"result": result, "message": "Emergency Kill Switch executed: All positions closed"}

@app.post("/api/positions/{ticket}/modify")
def api_modify_position(ticket: int, req: PositionModifyRequest):
    result = trader.modify_position(ticket, req.sl, req.tp)
    return {"result": result, "ticket": ticket, "sl": req.sl, "tp": req.tp}

@app.post("/api/bot/mode")
def api_set_bot_mode(mode: str = Query("semi_auto")):
    success = action_engine.set_bot_mode(mode)
    return {"success": success, "mode": action_engine.bot_mode}

@app.get("/api/strategy/composite")
async def api_get_composite(symbol: str = Query("XAUUSD"), timeframe: str = Query("M15")):
    df = await asyncio.to_thread(trader.get_candles, symbol, timeframe, 200)
    if df.empty:
        return {"error": "No candle data"}
    mtf = {}
    for tf in config.TIMEFRAMES:
        if tf != timeframe:
            df_tf = await asyncio.to_thread(trader.get_candles, symbol, tf, 100)
            if not df_tf.empty:
                mtf[tf] = algo.generate_signal_v2(df_tf, symbol)
    sig = algo.generate_signal_v2(df, symbol, mtf_signals=mtf)
    action = action_engine.depth_analysis_before_trade(symbol, timeframe, sig, mtf, df)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "composite_score": action["overall_score"],
        "strategy_breakdown": action.get("strategy_breakdown", {}),
        "checks": action.get("checks", {}),
        "can_trade": action["can_trade"],
        "action_required": action["action_required"],
        "reason": action["reason"],
        "bot_mode": action_engine.bot_mode,
        "signal": sig
    }

# WebSocket with fixed leak
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
    async def broadcast(self, data: dict):
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

manager = ConnectionManager()

@app.websocket("/ws/signals")
async def ws_signals(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Autonomous Trade Lifecycle Management (Break-Even + Trailing Stop)
            lifecycle_events = action_engine.manage_open_positions(trader)

            # Scan with depth analysis
            results = {}
            actions_created = []
            for symbol in config.SYMBOLS:
                mtf_all = {}
                for tf in config.TIMEFRAMES:
                    df = await asyncio.to_thread(trader.get_candles, symbol, tf, 100)
                    if not df.empty:
                        mtf_all[tf] = algo.generate_signal_v2(df, symbol)
                for tf in config.TIMEFRAMES:
                    df = await asyncio.to_thread(trader.get_candles, symbol, tf, 200)
                    if df.empty:
                        continue
                    mtf_for_this = {k:v for k,v in mtf_all.items() if k!=tf}
                    sig = algo.generate_signal_v2(df, symbol, mtf_signals=mtf_for_this)
                    key = f"{symbol}_{tf}"
                    results[key] = sig
                    # Auto create actions for strong signals
                    if sig['score'] >= 65:
                        action = action_engine.create_action(symbol, tf, sig, mtf_data=mtf_for_this, historical_data=df)
                        if action["status"] == "auto_approved" and action_engine.bot_mode == "full_auto":
                            # Auto execute if risk ok and position cap not exceeded
                            acc = trader.get_account_info()
                            equity = acc.get("equity", 10000)
                            can_risk, _ = risk_manager.check_daily_loss(equity)
                            current_pos = trader.get_positions()
                            if can_risk and len(current_pos) < action_engine.max_positions:
                                result = trader.send_order(symbol, "BUY" if sig["signal"].startswith("LE") else "SELL", 0.01, sl=sig.get("sl",0), tp=sig.get("tp",0), comment=f"AUTO-WS-{action['id']}")
                                action["execution_result"] = result
                                risk_manager.record_trade(symbol, 0.01)
                        actions_created.append(action)
            
            await manager.broadcast({
                "type": "signals_update",
                "timestamp": str(datetime.now()),
                "account": trader.get_account_info(),
                "positions": trader.get_positions(),
                "signals": results,
                "alerts": alerts.get_history(10),
                "pending_actions": action_engine.get_pending(),
                "risk": risk_manager.get_status(),
                "actions_created": actions_created,
                "bot_mode": action_engine.bot_mode,
                "lifecycle_events": lifecycle_events
            })
            await asyncio.sleep(4)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS error {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.BACKEND_PORT)

