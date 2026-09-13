"""
Super Algo Engine - XAU-GOD v1 / BTC-GOD v1
Implements MACD WITH LE/SE super prediction + Candle Depth + SR + Top/Bottom matching
"""
import pandas as pd
import numpy as np

class SuperAlgo:
    def __init__(self):
        pass

    def ema(self, series, period):
        return series.ewm(span=period, adjust=False).mean()

    def atr(self, df, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_indicators(self, df, fast=7, slow=26, signal=9):
        """Gold optimized fast 5-9 best per MDPI research"""
        df = df.copy()
        df['ema_fast'] = self.ema(df['close'], fast)
        df['ema_slow'] = self.ema(df['close'], slow)
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = self.ema(df['macd_line'], signal)
        df['histogram'] = df['macd_line'] - df['signal_line']
        df['rsi'] = self.rsi(df['close'], 14)
        df['atr'] = self.atr(df, 14)
        df['ema_21'] = self.ema(df['close'], 21)
        df['ema_50'] = self.ema(df['close'], 50)
        df['ema_200'] = self.ema(df['close'], 200)
        # Bollinger
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2*df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2*df['bb_std']
        return df

    def candle_depth(self, row):
        """Calculate candle depth metrics"""
        body = abs(row['close'] - row['open'])
        range_ = row['high'] - row['low']
        if range_ == 0:
            return {"body_ratio": 0, "type": "doji"}
        body_ratio = body / range_
        upper_wick = row['high'] - max(row['open'], row['close'])
        lower_wick = min(row['open'], row['close']) - row['low']
        
        if body_ratio < 0.3:
            ctype = "doji"
        elif row['close'] > row['open'] and body_ratio > 0.7:
            ctype = "strong_bull"
        elif row['close'] < row['open'] and body_ratio > 0.7:
            ctype = "strong_bear"
        elif upper_wick > body*2 and lower_wick < body*0.5:
            ctype = "gravestone"
        elif lower_wick > body*2 and upper_wick < body*0.5:
            ctype = "hammer"
        else:
            ctype = "normal"
        
        return {"body_ratio": body_ratio, "upper_wick": upper_wick, "lower_wick": lower_wick, "type": ctype}

    def detect_sr_zones(self, df, lookback=50):
        """Simple pivot based SR detection"""
        recent = df.tail(lookback)
        highs = recent['high'].nlargest(3).tolist()
        lows = recent['low'].nsmallest(3).tolist()
        return {"resistance": highs, "support": lows, "last_top": max(highs), "last_bottom": min(lows)}

    def generate_signal(self, df, symbol="XAUUSD"):
        """
        Returns super prediction signal dict
        LE = Long Entry, SE = Short Entry
        """
        if len(df) < 60:
            return {"signal": "NEUTRAL", "score": 0, "reason": "Not enough data"}

        df = self.calculate_indicators(df, fast=7 if "XAU" in symbol else 12, slow=26, signal=9)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Candle depth
        depth = self.candle_depth(last)
        sr = self.detect_sr_zones(df)
        
        # MACD LE/SE Logic - Gold Optimized
        le_conditions = []
        se_conditions = []
        
        # Zero-line cross - more significant than signal cross
        macd_zero_cross_up = prev['macd_line'] < 0 and last['macd_line'] > 0
        macd_zero_cross_down = prev['macd_line'] > 0 and last['macd_line'] < 0
        macd_above_signal = last['macd_line'] > last['signal_line']
        macd_below_signal = last['macd_line'] < last['signal_line']
        
        # Price vs EMAs
        price_above_200 = last['close'] > last['ema_200']
        price_below_200 = last['close'] < last['ema_200']
        ema21_above_50 = last['ema_21'] > last['ema_50']
        
        # RSI
        rsi_bull = last['rsi'] > 50
        rsi_bear = last['rsi'] < 50
        rsi_div_bear = last['rsi'] < 70 and df['rsi'].iloc[-5:].max() > 75  # potential top
        
        # Volume (use tick volume)
        volume_spike = last['volume'] > df['volume'].rolling(20).mean().iloc[-1] * 1.5
        
        # Top/Bottom matching logic
        distance_to_last_top = abs(last['close'] - sr['last_top']) / last['atr'] if last['atr']>0 else 999
        distance_to_last_bottom = abs(last['close'] - sr['last_bottom']) / last['atr'] if last['atr']>0 else 999
        
        near_top = distance_to_last_top < 0.5
        near_bottom = distance_to_last_bottom < 0.5
        
        # LE Scoring (0-100)
        le_score = 0
        if macd_zero_cross_up: le_score += 25
        if macd_above_signal: le_score += 15
        if price_above_200: le_score += 10
        if ema21_above_50: le_score += 10
        if rsi_bull: le_score += 10
        if depth['type'] in ['hammer','strong_bull']: le_score += 10
        if near_bottom: le_score += 10
        if volume_spike and last['close'] > last['open']: le_score += 10
        
        # SE Scoring
        se_score = 0
        if macd_zero_cross_down: se_score += 25
        if macd_below_signal: se_score += 15
        if price_below_200: se_score += 10
        if not ema21_above_50: se_score += 10
        if rsi_bear: se_score += 10
        if depth['type'] in ['gravestone','strong_bear']: se_score += 10
        if near_top: se_score += 15
        if volume_spike and last['close'] < last['open']: se_score += 10
        
        # Double top / bottom protection
        if near_top and rsi_div_bear:
            le_score -= 20
            se_score += 10
        
        # Final signal
        if le_score >= 70:
            signal = "LE"
        elif se_score >= 70:
            signal = "SE"
        elif le_score >= 50 and le_score > se_score:
            signal = "LE_WEAK"
        elif se_score >= 50 and se_score > le_score:
            signal = "SE_WEAK"
        else:
            signal = "NEUTRAL"
        
        # SL/TP based on ATR
        atr = last['atr']
        if np.isnan(atr):
            atr = last['close']*0.005
        
        if signal.startswith("LE"):
            sl = last['close'] - atr*1.5
            tp = last['close'] + atr*3.0
        elif signal.startswith("SE"):
            sl = last['close'] + atr*1.5
            tp = last['close'] - atr*3.0
        else:
            sl = 0
            tp = 0
        
        return {
            "signal": signal,
            "le_score": le_score,
            "se_score": se_score,
            "score": max(le_score, se_score),
            "price": float(last['close']),
            "rsi": float(last['rsi']),
            "macd": float(last['macd_line']),
            "signal_line": float(last['signal_line']),
            "histogram": float(last['histogram']),
            "atr": float(atr),
            "sl": float(sl),
            "tp": float(tp),
            "candle_type": depth['type'],
            "body_ratio": float(depth['body_ratio']),
            "near_top": bool(near_top),
            "near_bottom": bool(near_bottom),
            "last_top": float(sr['last_top']),
            "last_bottom": float(sr['last_bottom']),
            "reason": f"MACD zero cross:{macd_zero_cross_up}/{macd_zero_cross_down} RSI:{last['rsi']:.1f} Candle:{depth['type']} TopDist:{distance_to_last_top:.1f}ATR",
            "timestamp": str(df.iloc[-1]['time'])
        }
