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
        self.mock_balance = 10000.0
        self.mock_equity = 10000.0
        self.positions = []
        self.last_error = None

    def connect(self):
        if not MT5_AVAILABLE:
            print("[MOCK MODE] MT5 not available on this OS - running with synthetic data for dashboard dev")
            self.connected = True
            return True
        try:
            import MetaTrader5 as mt5
            mt5.initialize(path=self.config.MT5_PATH if self.config.MT5_PATH else None)
            authorized = mt5.login(self.config.MT5_LOGIN, password=self.config.MT5_PASSWORD, server=self.config.MT5_SERVER)
            if not authorized:
                self.last_error = f"Login failed: {mt5.last_error()}"
                print(self.last_error)
                return False
            self.connected = True
            print(f"MT5 Connected: {self.config.MT5_SERVER} - {self.config.MT5_LOGIN}")
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"MT5 connect error: {e}")
            return False

    def get_account_info(self):
        if not MT5_AVAILABLE:
            return {
                "login": 12345678,
                "server": "MOCK-DEMO",
                "balance": self.mock_balance,
                "equity": self.mock_equity + np.random.randn()*20,
                "profit": np.random.randn()*10,
                "leverage": 500,
                "currency": "USD",
                "connected": self.connected,
                "mode": "MOCK"
            }
        try:
            import MetaTrader5 as mt5
            acc = mt5.account_info()
            if acc is None:
                return None
            return {
                "login": acc.login,
                "server": acc.server,
                "balance": acc.balance,
                "equity": acc.equity,
                "profit": acc.profit,
                "leverage": acc.leverage,
                "currency": "USD",
                "connected": True,
                "mode": "REAL-DEMO"
            }
        except Exception as e:
            return {"error": str(e), "connected": False}

    def get_candles(self, symbol, timeframe="M15", count=300):
        """Returns DataFrame OHLCV"""
        tf_map = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}
        minutes = tf_map.get(timeframe, 15)
        
        if not MT5_AVAILABLE:
            # Generate realistic synthetic candles for dev
            np.random.seed(hash(symbol+timeframe) % 1000)
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

        try:
            import MetaTrader5 as mt5
            tf_enum = {
                "M15": mt5.TIMEFRAME_M15,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }.get(timeframe, mt5.TIMEFRAME_M15)
            rates = mt5.copy_rates(symbol, tf_enum, 0, count)
            if rates is None or len(rates)==0:
                return pd.DataFrame()
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.rename(columns={"tick_volume": "volume"}, inplace=True)
            return df
        except Exception as e:
            print(f"get_candles error {e}")
            return pd.DataFrame()

    def get_positions(self):
        if not MT5_AVAILABLE:
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
        if not MT5_AVAILABLE:
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
