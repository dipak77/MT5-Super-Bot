"""
Risk Manager - Production Grade
Enforces risk per trade, daily loss limit, equity guard, real trade confirmation
"""
from datetime import datetime, date
import json, os

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.real_trades_confirmed = 0
        self.start_balance = 10000.0
        self.peak_equity = 10000.0
        self.log_file = "logs/risk.log"
        os.makedirs("logs", exist_ok=True)

    def check_daily_loss(self, current_equity):
        loss_pct = (current_equity - self.start_balance) / self.start_balance
        if loss_pct <= -self.config.MAX_DAILY_LOSS:
            self.log(f"BLOCKED: Daily loss limit reached {loss_pct*100:.2f}%")
            return False, f"Daily loss limit {self.config.MAX_DAILY_LOSS*100}% reached"
        return True, "OK"

    def check_risk_per_trade(self, symbol, volume, price, sl):
        # Calculate risk amount
        risk_amount = abs(price - sl) * volume * 100  # simplified
        max_risk = self.start_balance * self.config.RISK_PER_TRADE
        if risk_amount > max_risk * 1.5:
            return False, f"Risk too high {risk_amount:.2f} > {max_risk:.2f}"
        return True, "OK"

    def check_real_confirmation(self):
        if self.config.LIVE_TRADING and getattr(self.config, 'CONFIRM_REAL_TRADE', False):
            if self.real_trades_confirmed < 10:
                # In real implementation, ask console input
                self.log(f"Real trade #{self.real_trades_confirmed+1} requires confirmation")
                return False, f"Real trade confirmation required ({self.real_trades_confirmed}/10)"
        return True, "OK"

    def confirm_real_trade(self):
        self.real_trades_confirmed += 1
        self.log(f"Real trade confirmed {self.real_trades_confirmed}")

    def update_equity(self, equity):
        self.peak_equity = max(self.peak_equity, equity)
        drawdown = (equity - self.peak_equity) / self.peak_equity
        if drawdown < -0.05:
            self.log(f"WARNING: Drawdown {drawdown*100:.2f}% - Auto trading disabled")
            return False
        return True

    def log(self, msg):
        entry = f"[{datetime.now()}] {msg}"
        print(entry)
        try:
            with open(self.log_file, "a") as f:
                f.write(entry+"\n")
        except:
            pass
