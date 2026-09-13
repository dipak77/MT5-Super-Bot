"""
MT5 Connector - Works on Windows with real MT5, and in mock mode on Linux/Mac for dev
"""
import sys
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

IS_WINDOWS = sys.platform == "win32"

try:
    if IS_WINDOWS:
        import MetaTrader5 as mt5
        MT5_AVAILABLE = True
    else:
        MT5_AVAILABLE = False
except:
    MT5_AVAILABLE = False

class MT5Trader:
    def __init__(self, config):
        self.config = config
        self.connected = False
        start_bal = float(getattr(self.config, 'START_BALANCE', 100000.0))
        self.mock_balance = start_bal
        self.mock_equity = start_bal
        self.positions = []
        self.last_error = None

    def connect(self):
        if not MT5_AVAILABLE:
            print("[DEMO-SYNC] MT5 package not available - running in synchronized demo mode")
            self.connected = False
            return False
        try:
            import MetaTrader5 as mt5
            init_kwargs = {}
            if getattr(self.config, 'MT5_PATH', None):
                init_kwargs["path"] = self.config.MT5_PATH
            init_ok = mt5.initialize(**init_kwargs)
            if not init_ok:
                self.last_error = f"MT5 initialize failed: {mt5.last_error()}"
                print(f"[MT5] {self.last_error} - falling back to demo-account sync mode")
                self.connected = False
                return False

            login_val = int(self.config.MT5_LOGIN) if self.config.MT5_LOGIN else 0
            pwd_val = str(self.config.MT5_PASSWORD)
            srv_val = str(self.config.MT5_SERVER)
            authorized = mt5.login(login=login_val, password=pwd_val, server=srv_val)
            if not authorized:
                self.last_error = f"MT5 login failed: {mt5.last_error()}"
                print(f"[MT5] {self.last_error}")
                self.connected = False
                return False
            self.connected = True
            print(f"[MT5] Connected successfully: {srv_val} - Login: {login_val}")
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"[MT5] Connect error: {e}")
            self.connected = False
            return False

    def _mock_account(self):
        login = self.config.MT5_LOGIN if self.config.MT5_LOGIN else 112559567
        server = self.config.MT5_SERVER if self.config.MT5_SERVER else "MetaQuotes-Demo"
        name = getattr(self.config, 'ACCOUNT_NAME', "Dipak Harane")
        account_type = getattr(self.config, 'ACCOUNT_TYPE', "Forex Hedged USD")
        pos_profit = sum(p.get("profit", 0.0) for p in self.positions)
        return {
            "login": login,
            "server": server,
            "name": name,
            "account_type": account_type,
            "balance": round(self.mock_balance, 2),
            "equity": round(self.mock_equity + pos_profit, 2),
            "profit": round(pos_profit, 2),
            "leverage": 500,
            "currency": "USD",
            "connected": self.connected,
            "mode": "REAL-DEMO" if self.connected else "DEMO-ACCOUNT"
        }

    def get_account_info(self):
        if not MT5_AVAILABLE or not self.connected:
            return self._mock_account()
        try:
            import MetaTrader5 as mt5
            acc = mt5.account_info()
            if acc is None:
                return self._mock_account()
            return {
                "login": acc.login,
                "server": acc.server,
                "name": getattr(acc, "name", getattr(self.config, "ACCOUNT_NAME", "Dipak Harane")),
                "account_type": getattr(self.config, "ACCOUNT_TYPE", "Forex Hedged USD"),
                "balance": acc.balance,
                "equity": acc.equity,
                "profit": acc.profit,
                "leverage": acc.leverage,
                "currency": getattr(acc, "currency", "USD"),
                "connected": True,
                "mode": "REAL-DEMO"
            }
        except Exception as e:
            return {"error": str(e), "connected": False}

    def _mock_candles(self, symbol, timeframe="M15", count=300):
        """Generate realistic synthetic candles for dev / fallback when MT5 terminal not connected"""
        tf_map = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}
        minutes = tf_map.get(timeframe, 15)
        np.random.seed(abs(hash(symbol+timeframe)) % 1000)
        base_price = 4320 if "XAU" in symbol else 77172
        dates = [datetime.now() - timedelta(minutes=minutes*i) for i in range(count)][::-1]
        closes = []
        price = base_price
        for i in range(count):
            price += np.random.randn()* (base_price*0.0005)
            # Add trend and support/resistance bounce
            if i % 80 == 0:
                price += np.random.choice([-1,1]) * base_price*0.01
            closes.append(price)
        df = pd.DataFrame({
            "time": dates,
            "open": [c + np.random.randn()*2 for c in closes],
            "high": [c + abs(np.random.randn()*5) for c in closes],
            "low": [c - abs(np.random.randn()*5) for c in closes],
            "close": closes,
            "volume": [int(abs(np.random.randn()*1000)+500) for _ in closes]
        })
        # Ensure high/low consistency
        df["high"] = df[["open","close","high"]].max(axis=1)
        df["low"] = df[["open","close","low"]].min(axis=1)
        return df

    def get_candles(self, symbol, timeframe="M15", count=300):
        """Returns DataFrame OHLCV"""
        if not MT5_AVAILABLE:
            return self._mock_candles(symbol, timeframe, count)

        try:
            import MetaTrader5 as mt5
            tf_enum = {
                "M15": mt5.TIMEFRAME_M15,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }.get(timeframe, mt5.TIMEFRAME_M15)
            # NOTE: copy_rates was removed in newer MT5 builds, use copy_rates_from_pos
            copy_fn = getattr(mt5, "copy_rates_from_pos", None) or getattr(mt5, "copy_rates", None)
            if copy_fn is None:
                print("MT5 has no copy_rates API, falling back to mock")
                return self._mock_candles(symbol, timeframe, count)
            rates = copy_fn(symbol, tf_enum, 0, count)
            if rates is None or len(rates)==0:
                # Terminal not connected / no data -> fallback to mock so dashboard/dev still works
                print(f"MT5 no data for {symbol} {timeframe} (terminal not connected?), using mock candles")
                return self._mock_candles(symbol, timeframe, count)
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            if "tick_volume" in df.columns:
                df.rename(columns={"tick_volume": "volume"}, inplace=True)
            if "volume" not in df.columns:
                df["volume"] = 500
            return df
        except Exception as e:
            print(f"get_candles error {e}, falling back to mock")
            return self._mock_candles(symbol, timeframe, count)

    def get_positions(self):
        if not MT5_AVAILABLE or not self.connected:
            return self.positions
        try:
            import MetaTrader5 as mt5
            pos = mt5.positions_get()
            if pos is None:
                return []
            return [{
                "ticket": p.ticket,
                "symbol": p.symbol,
                "type": "BUY" if p.type==0 else "SELL",
                "volume": p.volume,
                "price_open": p.price_open,
                "price_current": p.price_current,
                "profit": p.profit,
                "sl": p.sl,
                "tp": p.tp,
                "time": str(datetime.fromtimestamp(p.time))
            } for p in pos]
        except Exception as e:
            return []

    def send_order(self, symbol, order_type, volume=0.01, sl=0, tp=0, comment="XAU-GOD v1"):
        """order_type: BUY or SELL"""
        if not MT5_AVAILABLE or not self.connected:
            ticket = int(time.time())
            entry_price = 4320 if "XAU" in symbol else 77172
            new_pos = {
                "ticket": ticket,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "price_open": entry_price,
                "price_current": entry_price,
                "profit": 0.0,
                "sl": sl,
                "tp": tp,
                "time": str(datetime.now())
            }
            self.positions.append(new_pos)
            print(f"[MOCK ORDER] {order_type} {symbol} {volume} SL:{sl} TP:{tp}")
            return {"retcode": 10009, "ticket": ticket, "mock": True}

        try:
            import MetaTrader5 as mt5
            price = mt5.symbol_info_tick(symbol).ask if order_type=="BUY" else mt5.symbol_info_tick(symbol).bid
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type=="BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 20260913,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            return {"retcode": result.retcode, "ticket": result.order, "result": str(result)}
        except Exception as e:
            return {"error": str(e), "retcode": -1}

    def close_position(self, ticket):
        """Close a specific position by ticket"""
        if not MT5_AVAILABLE or not self.connected:
            for i, p in enumerate(self.positions):
                if p["ticket"] == ticket:
                    closed = self.positions.pop(i)
                    print(f"[MOCK CLOSE] Closed ticket {ticket} ({closed.get('symbol')} {closed.get('type')})")
                    return {"retcode": 10009, "ticket": ticket, "closed": True, "mock": True}
            return {"retcode": -1, "error": f"Ticket {ticket} not found"}

        try:
            import MetaTrader5 as mt5
            pos = mt5.positions_get(ticket=ticket)
            if not pos or len(pos) == 0:
                return {"retcode": -1, "error": f"Position {ticket} not found"}
            p = pos[0]
            close_type = mt5.ORDER_TYPE_SELL if p.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(p.symbol).bid if p.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(p.symbol).ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": p.symbol,
                "volume": p.volume,
                "type": close_type,
                "price": price,
                "deviation": 20,
                "magic": 20260913,
                "comment": "CLOSE-BOT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            return {"retcode": result.retcode, "ticket": ticket, "result": str(result)}
        except Exception as e:
            return {"error": str(e), "retcode": -1}

    def close_all_positions(self):
        """Emergency Kill Switch - close all open positions"""
        positions = self.get_positions()
        results = []
        for p in positions:
            res = self.close_position(p["ticket"])
            results.append({"ticket": p["ticket"], "result": res})
        return {"closed_count": len(results), "details": results}

    def modify_position(self, ticket, sl, tp):
        """Modify Stop Loss and Take Profit for Break-Even / Trailing Stop"""
        if not MT5_AVAILABLE or not self.connected:
            for p in self.positions:
                if p["ticket"] == ticket:
                    p["sl"] = float(sl)
                    p["tp"] = float(tp)
                    print(f"[MOCK MODIFY] Ticket {ticket} new SL:{sl} TP:{tp}")
                    return {"retcode": 10009, "ticket": ticket, "sl": sl, "tp": tp, "mock": True}
            return {"retcode": -1, "error": f"Ticket {ticket} not found"}

        try:
            import MetaTrader5 as mt5
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": float(sl),
                "tp": float(tp),
            }
            result = mt5.order_send(request)
            return {"retcode": result.retcode, "ticket": ticket, "sl": sl, "tp": tp, "result": str(result)}
        except Exception as e:
            return {"error": str(e), "retcode": -1}

