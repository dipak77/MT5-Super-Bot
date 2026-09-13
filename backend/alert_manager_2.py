import requests
from datetime import datetime

class AlertManager:
    def __init__(self, config):
        self.config = config
        self.alerts_history = []

    def send_telegram(self, message):
        if not self.config.TELEGRAM_TOKEN or not self.config.TELEGRAM_CHAT_ID:
            print(f"[TELEGRAM MOCK] {message}")
            return False
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_TOKEN}/sendMessage"
            data = {"chat_id": self.config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            r = requests.post(url, json=data, timeout=5)
            return r.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    def create_alert(self, symbol, signal_data):
        alert = {
            "id": len(self.alerts_history)+1,
            "symbol": symbol,
            "signal": signal_data['signal'],
            "price": signal_data['price'],
            "score": signal_data['score'],
            "reason": signal_data['reason'],
            "sl": signal_data['sl'],
            "tp": signal_data['tp'],
            "timestamp": str(datetime.now()),
            "candle_type": signal_data['candle_type']
        }
        self.alerts_history.insert(0, alert)
        # Keep only last 100
        self.alerts_history = self.alerts_history[:100]

        # Send telegram for strong signals
        if signal_data['score'] >= 70:
            msg = f"🚨 *SUPER SIGNAL* {symbol}\nSignal: {signal_data['signal']} Score:{signal_data['score']}\nPrice: {signal_data['price']}\nRSI:{signal_data['rsi']:.1f} MACD:{signal_data['macd']:.4f}\nCandle: {signal_data['candle_type']}\nSL:{signal_data['sl']:.2f} TP:{signal_data['tp']:.2f}\nReason: {signal_data['reason']}"
            self.send_telegram(msg)
        
        return alert

    def get_history(self, limit=50):
        return self.alerts_history[:limit]
