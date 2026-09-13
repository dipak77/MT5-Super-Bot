"""
FastAPI Backend - MT5 Super Bot API
Provides real-time account, candles, signals, positions, and WebSocket for alerts
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
from config import config
from mt5_trader import MT5Trader
from super_algo import SuperAlgo
from alert_manager import AlertManager

app = FastAPI(title="MT5 Super Bot - XAU-GOD / BTC-GOD v1", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trader = MT5Trader(config)
algo = SuperAlgo()
alerts = AlertManager(config)

# Connect on startup
@app.on_event("startup")
async def startup():
    trader.connect()

@app.get("/")
def root():
    return {"message": "MT5 Super Bot API Running", "symbols": config.SYMBOLS, "timeframes": config.TIMEFRAMES, "mode": "MOCK" if trader.get_account_info().get("mode")=="MOCK" else "REAL-DEMO"}

@app.get("/api/account")
def get_account():
    return trader.get_account_info()

@app.get("/api/positions")
def get_positions():
    return {"positions": trader.get_positions(), "count": len(trader.get_positions())}

@app.get("/api/candles")
def get_candles(symbol: str = Query("XAUUSD"), timeframe: str = Query("M15"), count: int = Query(300)):
    df = trader.get_candles(symbol, timeframe, count)
    if df.empty:
        return {"error": "No data", "symbol": symbol, "timeframe": timeframe}
    # Add indicators for frontend
    df_ind = algo.calculate_indicators(df)
    # Convert to list for JSON
    candles = df_ind.tail(200).to_dict(orient="records")
    # Convert timestamps to string
    for c in candles:
        c['time'] = str(c['time'])
        for k in c:
            if isinstance(c[k], (float)) and (c[k] != c[k]): # NaN check
                c[k] = None
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles, "count": len(candles)}

@app.get("/api/signal")
def get_signal(symbol: str = Query("XAUUSD"), timeframe: str = Query("M15")):
    df = trader.get_candles(symbol, timeframe, 200)
    if df.empty:
        return {"error": "No data"}
    sig = algo.generate_signal(df, symbol)
    return {"symbol": symbol, "timeframe": timeframe, "signal": sig}

@app.get("/api/signals/all")
def get_all_signals():
    results = {}
    for symbol in config.SYMBOLS:
        results[symbol] = {}
        for tf in config.TIMEFRAMES:
            df = trader.get_candles(symbol, tf, 200)
            if not df.empty:
                sig = algo.generate_signal(df, symbol)
                results[symbol][tf] = sig
    return results

@app.get("/api/alerts")
def get_alerts(limit: int = 50):
    return {"alerts": alerts.get_history(limit)}

@app.post("/api/execute")
def execute_trade(symbol: str, type: str, volume: float = 0.01):
    """Execute trade - type BUY/SELL"""
    if not config.AUTO_TRADING and not config.LIVE_TRADING:
        # In demo safe mode, check if request is from dashboard test
        pass
    
    # Get latest signal for SL/TP
    df = trader.get_candles(symbol, "M15", 100)
    sig = algo.generate_signal(df, symbol) if not df.empty else {"sl":0,"tp":0}
    
    result = trader.send_order(symbol, type, volume, sl=sig.get("sl",0), tp=sig.get("tp",0))
    return {"result": result, "symbol": symbol, "type": type, "volume": volume}

@app.post("/api/scan")
def scan_markets():
    """Scan all symbols and timeframes and create alerts for strong signals"""
    new_alerts = []
    for symbol in config.SYMBOLS:
        for tf in config.TIMEFRAMES:
            df = trader.get_candles(symbol, tf, 200)
            if df.empty:
                continue
            sig = algo.generate_signal(df, symbol)
            if sig['score'] >= 70:
                alert = alerts.create_alert(f"{symbol}-{tf}", sig)
                new_alerts.append(alert)
    return {"new_alerts": new_alerts, "scanned": f"{len(config.SYMBOLS)*len(config.TIMEFRAMES)} pairs"}

# WebSocket for realtime alerts
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
        for ws in self.active:
            try:
                await ws.send_json(data)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/signals")
async def ws_signals(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Every 5 seconds scan and broadcast
            results = {}
            for symbol in config.SYMBOLS:
                for tf in config.TIMEFRAMES:
                    df = trader.get_candles(symbol, tf, 200)
                    if df.empty:
                        continue
                    sig = algo.generate_signal(df, symbol)
                    key = f"{symbol}_{tf}"
                    results[key] = sig
                    if sig['score'] >= 70:
                        alerts.create_alert(f"{symbol}-{tf}", sig)
            await manager.broadcast({
                "type": "signals_update",
                "timestamp": str(datetime.now()),
                "account": trader.get_account_info(),
                "positions": trader.get_positions(),
                "signals": results,
                "alerts": alerts.get_history(10)
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS error {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.BACKEND_PORT)
