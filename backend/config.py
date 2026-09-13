import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "")
    MT5_PATH = os.getenv("MT5_PATH", "")
    SYMBOLS = os.getenv("SYMBOLS", "XAUUSD,BTCUSD").split(",")
    TIMEFRAMES = os.getenv("TIMEFRAMES", "M15,H1,H4,D1").split(",")
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.005"))
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "0.03"))
    ATR_SL = float(os.getenv("ATR_MULTIPLIER_SL", "1.5"))
    ATR_TP = float(os.getenv("ATR_MULTIPLIER_TP", "3.0"))
    LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"
    AUTO_TRADING = os.getenv("AUTO_TRADING", "false").lower() == "true"
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

config = Config()
