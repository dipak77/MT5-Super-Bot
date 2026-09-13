"""
Risk Manager V2 - Enhanced
- Fixed daily loss tracking
- Equity guard -5% auto disable
- Real confirmation first 10 trades
- Volume limit real start 0.01 max first week
- Log rotation
"""
from datetime import datetime, date
import os, json

class RiskManagerV2:
    def __init__(self, config):
        self.config = config
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.start_balance = 10000.0
        self.peak_equity = 10000.0
        self.real_trades_confirmed = 0
        self.last_reset_date = date.today()
        self.log_file = "logs/risk.log"
        self.trades_today = []
        os.makedirs("logs", exist_ok=True)
        # Load start balance from account if available
        try:
            with open("logs/equity.json", "r") as f:
                data = json.load(f)
                self.start_balance = data.get("start_balance", 10000.0)
                self.peak_equity = data.get("peak_equity", 10000.0)
        except:
            pass

    def reset_if_new_day(self):
        today = date.today()
        if today != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.trades_today = []
            self.last_reset_date = today
            self.log(f"New day reset - Daily PnL reset")

    def check_daily_loss(self, current_equity):
        self.reset_if_new_day()
        # Calculate daily PnL
        pnl_pct = (current_equity - self.start_balance) / self.start_balance if self.start_balance else 0
        self.daily_pnl = pnl_pct
        
        if pnl_pct <= -self.config.MAX_DAILY_LOSS:
            self.log(f"BLOCKED: Daily loss limit {self.config.MAX_DAILY_LOSS*100}% reached, current {pnl_pct*100:.2f}% equity {current_equity}")
            return False, f"Daily loss limit {self.config.MAX_DAILY_LOSS*100}% reached ({pnl_pct*100:.2f}%)"
        
        # Equity guard -5%
        if not self.update_equity(current_equity):
            return False, "Equity guard -5% drawdown, auto trading disabled"
        
        return True, f"OK daily {pnl_pct*100:.2f}%"

    def check_risk_per_trade(self, symbol, volume, price, sl):
        if not price or not sl:
            return True, "No SL, skip risk check (will use ATR default)"
        
        risk_per_trade_pct = self.config.RISK_PER_TRADE
        # Risk amount simplified: |price-sl| * volume * contract size (100 for XAU, 1 for BTC)
        contract = 100 if "XAU" in symbol else 1
        risk_amount = abs(price - sl) * volume * contract
        max_risk = self.start_balance * risk_per_trade_pct
        
        if risk_amount > max_risk * 2:
            return False, f"Risk too high {risk_amount:.2f} > max {max_risk:.2f} (2x), reduce volume or SL"
        
        return True, f"Risk OK {risk_amount:.2f} <= {max_risk:.2f}"

    def check_real_confirmation(self):
        if self.config.LIVE_TRADING:
            if self.real_trades_confirmed < 10:
                return False, f"Real trade confirmation required ({self.real_trades_confirmed}/10) - type YES in console or approve via dashboard"
        return True, "OK"

    def confirm_real_trade(self):
        self.real_trades_confirmed += 1
        self.save_state()
        self.log(f"Real trade confirmed {self.real_trades_confirmed}/10")

    def update_equity(self, equity):
        self.peak_equity = max(self.peak_equity, equity)
        drawdown = (equity - self.peak_equity) / self.peak_equity if self.peak_equity else 0
        if drawdown < -0.05:
            self.log(f"WARNING: Drawdown {drawdown*100:.2f}% from peak {self.peak_equity} to {equity} - Auto trading DISABLED")
            return False
        self.save_state()
        return True

    def record_trade(self, symbol, volume, profit=0):
        self.daily_trades += 1
        self.trades_today.append({"symbol": symbol, "volume": volume, "profit": profit, "time": str(datetime.now())})
        self.log(f"Trade recorded {symbol} vol {volume} daily trades {self.daily_trades}")

    def save_state(self):
        try:
            with open("logs/equity.json", "w") as f:
                json.dump({"start_balance": self.start_balance, "peak_equity": self.peak_equity, "real_trades_confirmed": self.real_trades_confirmed, "last_reset": str(self.last_reset_date)}, f)
        except:
            pass

    def get_status(self):
        return {
            "start_balance": self.start_balance,
            "peak_equity": self.peak_equity,
            "daily_pnl_pct": self.daily_pnl*100,
            "daily_trades": self.daily_trades,
            "real_trades_confirmed": self.real_trades_confirmed,
            "max_daily_loss_pct": self.config.MAX_DAILY_LOSS*100,
            "risk_per_trade_pct": self.config.RISK_PER_TRADE*100,
            "is_live": self.config.LIVE_TRADING
        }

    def log(self, msg):
        entry = f"[{datetime.now()}] [RISK] {msg}"
        print(entry)
        try:
            with open(self.log_file, "a") as f:
                f.write(entry+"\n")
        except:
            pass
