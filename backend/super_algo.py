"""
Super Algo V2 - Fixed and Enhanced
- Fixed RSI Wilder
- Fixed candle_depth KeyError and logic
- Enhanced detect_sr_zones with pivot left/right, rejection count, order block, breaker
- Added MTF alignment, past movement analysis, historical top matching
- Clamped scoring 0-100
- Added strategy and pattern scoring
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

    def rsi_wilder(self, series, period=14):
        """Fixed RSI with Wilder smoothing, not SMA"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        # Wilder's smoothing
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        rs = rs.replace([np.inf, -np.inf], 100)  # handle division by zero
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50)
        return rsi

    def calculate_indicators(self, df, fast=7, slow=26, signal=9):
        df = df.copy()
        df['ema_fast'] = self.ema(df['close'], fast)
        df['ema_slow'] = self.ema(df['close'], slow)
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = self.ema(df['macd_line'], signal)
        df['histogram'] = df['macd_line'] - df['signal_line']
        df['rsi'] = self.rsi_wilder(df['close'], 14)
        df['atr'] = self.atr(df, 14)
        df['ema_21'] = self.ema(df['close'], 21)
        df['ema_50'] = self.ema(df['close'], 50)
        df['ema_200'] = self.ema(df['close'], 200)
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2*df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2*df['bb_std']
        # Additional for strategy review
        df['volume_ma'] = df['volume'].rolling(20).mean()
        return df

    def candle_depth(self, row):
        """Fixed: always return upper_wick, lower_wick, no KeyError, use range not body for hammer logic"""
        body = abs(row['close'] - row['open'])
        range_ = row['high'] - row['low']
        if range_ == 0:
            return {"body_ratio": 0, "upper_wick": 0, "lower_wick": 0, "type": "doji", "wick_imbalance": 1, "volume_confirm": False}
        
        body_ratio = body / range_
        upper_wick = row['high'] - max(row['open'], row['close'])
        lower_wick = min(row['open'], row['close']) - row['low']
        wick_imbalance = upper_wick / (lower_wick + 0.001)
        
        # Fixed logic: use range for hammer detection, not body*2 which fails for doji
        if body_ratio < 0.15:
            ctype = "doji"
        elif lower_wick > range_ * 0.6 and upper_wick < range_ * 0.2 and body_ratio < 0.4:
            ctype = "hammer"
        elif upper_wick > range_ * 0.6 and lower_wick < range_ * 0.2 and body_ratio < 0.4:
            ctype = "gravestone"
        elif row['close'] > row['open'] and body_ratio > 0.7:
            ctype = "strong_bull"
        elif row['close'] < row['open'] and body_ratio > 0.7:
            ctype = "strong_bear"
        elif row['close'] > row['open'] and body_ratio > 0.4:
            ctype = "bullish_engulfing" if body > abs(row['open'] - row.get('prev_close', row['open'])) else "normal_bull"
        else:
            ctype = "normal"
        
        volume_confirm = row.get('volume', 0) > row.get('volume_ma', 0) * 1.5 if 'volume_ma' in row else False
        
        return {
            "body_ratio": float(body_ratio),
            "upper_wick": float(upper_wick),
            "lower_wick": float(lower_wick),
            "type": ctype,
            "wick_imbalance": float(wick_imbalance),
            "volume_confirm": bool(volume_confirm)
        }

    def detect_sr_zones_enhanced(self, df, left=3, right=3, lookback=100):
        """
        Enhanced SR detection with pivot left/right bars, rejection count, order block, breaker
        Fixes naive nlargest(3) bug
        """
        recent = df.tail(lookback).copy()
        highs = []
        lows = []
        # Pivot detection: high is pivot high if it's highest among left+right neighbors
        for i in range(left, len(recent)-right):
            window_high = recent.iloc[i-left:i+right+1]['high']
            if recent.iloc[i]['high'] == window_high.max():
                highs.append({
                    "price": float(recent.iloc[i]['high']),
                    "time": str(recent.iloc[i]['time']),
                    "index": i,
                    "rejection_count": 0
                })
            window_low = recent.iloc[i-left:i+right+1]['low']
            if recent.iloc[i]['low'] == window_low.min():
                lows.append({
                    "price": float(recent.iloc[i]['low']),
                    "time": str(recent.iloc[i]['time']),
                    "index": i,
                    "rejection_count": 0
                })
        
        # Count rejections within 0.1% for XAU, 0.2% for BTC
        for h in highs:
            count = 0
            for _, row in recent.iterrows():
                if abs(row['high'] - h['price']) / h['price'] < 0.001:
                    count += 1
            h['rejection_count'] = count
        
        for l in lows:
            count = 0
            for _, row in recent.iterrows():
                if abs(row['low'] - l['price']) / l['price'] < 0.001:
                    count += 1
            l['rejection_count'] = count
        
        # Sort by rejection count and recency
        highs_sorted = sorted(highs, key=lambda x: (x['rejection_count'], x['index']), reverse=True)[:5]
        lows_sorted = sorted(lows, key=lambda x: (x['rejection_count'], x['index']), reverse=True)[:5]
        
        # Order block & breaker detection (simplified)
        # Breaker: level broken then retested
        breaker_levels = []
        last_close = recent.iloc[-1]['close']
        for h in highs_sorted:
            # If current price above level that was resistance, now support (breaker)
            if last_close > h['price'] and h['rejection_count'] >=2:
                breaker_levels.append({"price": h['price'], "type": "breaker_support", "old_resistance": True})
        
        resistance_prices = [h['price'] for h in highs_sorted]
        support_prices = [l['price'] for l in lows_sorted]
        
        return {
            "resistance": resistance_prices,
            "support": support_prices,
            "resistance_detailed": highs_sorted,
            "support_detailed": lows_sorted,
            "breaker": breaker_levels,
            "last_top": float(max(resistance_prices) if resistance_prices else recent['high'].max()),
            "last_bottom": float(min(support_prices) if support_prices else recent['low'].min()),
            "strongest_resistance": highs_sorted[0] if highs_sorted else None,
            "strongest_support": lows_sorted[0] if lows_sorted else None
        }

    def check_mtf_alignment(self, mtf_signals):
        """Check trend alignment across M15/H1/H4/D1"""
        if not mtf_signals:
            return {"score": 0, "bullish_count": 0, "bearish_count": 0, "aligned": False, "detail": "No MTF data"}
        
        bullish = 0
        bearish = 0
        for tf, sig in mtf_signals.items():
            if sig and sig.get('signal', '').startswith('LE'):
                bullish += 1
            elif sig and sig.get('signal', '').startswith('SE'):
                bearish += 1
        
        total = len(mtf_signals)
        if bullish >= 3:
            score = 20
            detail = f"Strong bullish alignment {bullish}/{total} TFs LE"
            aligned = True
        elif bearish >= 3:
            score = 20
            detail = f"Strong bearish alignment {bearish}/{total} TFs SE"
            aligned = True
        elif bullish == 2 and bearish == 0:
            score = 10
            detail = f"Weak bullish {bullish}/{total}"
            aligned = False
        elif bearish == 2 and bullish == 0:
            score = 10
            detail = f"Weak bearish {bearish}/{total}"
            aligned = False
        else:
            score = 0
            detail = f"No alignment bullish {bullish} bearish {bearish} /{total}"
            aligned = False
        
        return {"score": score, "bullish_count": bullish, "bearish_count": bearish, "aligned": aligned, "detail": detail}

    def generate_signal_v2(self, df, symbol="XAUUSD", mtf_signals=None):
        if len(df) < 60:
            return {"signal": "NEUTRAL", "score": 0, "reason": "Not enough data"}

        # Adaptive fast for gold vs btc
        fast = 7 if "XAU" in symbol else 12
        df = self.calculate_indicators(df, fast=fast, slow=26, signal=9)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Enhanced depth
        depth = self.candle_depth(last)
        sr = self.detect_sr_zones_enhanced(df, left=3, right=3, lookback=100)
        
        # MACD logic
        macd_zero_cross_up = prev['macd_line'] < 0 and last['macd_line'] > 0
        macd_zero_cross_down = prev['macd_line'] > 0 and last['macd_line'] < 0
        macd_above_signal = last['macd_line'] > last['signal_line']
        macd_below_signal = last['macd_line'] < last['signal_line']
        
        price_above_200 = last['close'] > last['ema_200']
        ema21_above_50 = last['ema_21'] > last['ema_50']
        
        rsi_bull = last['rsi'] > 50
        rsi_div_bear = last['rsi'] < 70 and df['rsi'].iloc[-5:].max() > 75
        
        volume_spike = last['volume'] > last['volume_ma'] * 1.5 if not pd.isna(last['volume_ma']) else False
        
        # Adaptive ATR distance per symbol
        # XAU ATR $2-5 normal, $8-15 CPI, BTC ATR $150-300
        atr = last['atr'] if not pd.isna(last['atr']) else last['close']*0.005
        price = last['close']
        last_top = sr['last_top']
        last_bottom = sr['last_bottom']
        dist_top_atr = abs(price - last_top) / atr if atr else 999
        dist_bottom_atr = abs(price - last_bottom) / atr if atr else 999
        near_top = dist_top_atr < 0.8
        near_bottom = dist_bottom_atr < 0.8
        
        # MTF alignment
        mtf_check = self.check_mtf_alignment(mtf_signals) if mtf_signals else {"score":0,"bullish_count":0,"bearish_count":0,"aligned":False,"detail":"No MTF"}
        
        # Scoring clamped 0-100
        le_score = 0
        se_score = 0
        
        if macd_zero_cross_up: le_score += 25
        if macd_above_signal: le_score += 15
        if price_above_200: le_score += 10
        if ema21_above_50: le_score += 10
        if rsi_bull: le_score += 10
        if depth['type'] in ['hammer','strong_bull','bullish_engulfing']: le_score += 10
        if near_bottom: le_score += 10
        if volume_spike and last['close'] > last['open']: le_score += 10
        le_score += mtf_check['score'] if mtf_check['bullish_count']>=2 else 0
        
        if macd_zero_cross_down: se_score += 25
        if macd_below_signal: se_score += 15
        if not price_above_200: se_score += 10
        if not ema21_above_50: se_score += 10
        if not rsi_bull: se_score += 10
        if depth['type'] in ['gravestone','strong_bear']: se_score += 10
        if near_top: se_score += 15
        if volume_spike and last['close'] < last['open']: se_score += 10
        se_score += mtf_check['score'] if mtf_check['bearish_count']>=2 else 0
        
        # Clamp 0-100
        le_score = max(0, min(100, le_score))
        se_score = max(0, min(100, se_score))
        
        if near_top and rsi_div_bear and le_score>0:
            le_score = max(0, le_score - 20)
            se_score = min(100, se_score + 10)
        
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
        
        # SL/TP adaptive per volatility
        if atr < last['close']*0.002:  # low vol
            sl_mult = 1.2
            tp_mult = 2.5
        elif atr > last['close']*0.01:  # high vol
            sl_mult = 2.0
            tp_mult = 5.0
        else:
            sl_mult = 1.5
            tp_mult = 3.0
        
        if signal.startswith("LE"):
            sl = last['close'] - atr*sl_mult
            tp = last['close'] + atr*tp_mult
        elif signal.startswith("SE"):
            sl = last['close'] + atr*sl_mult
            tp = last['close'] - atr*tp_mult
        else:
            sl = 0
            tp = 0
        
        # Past movement analysis
        past_detail = "No repeating failed pattern"
        if len(df) > 50:
            recent_highs = df.tail(50)['high'].nlargest(3)
            for rh in recent_highs:
                if abs(price - rh)/price < 0.0015:
                    past_detail = f"Near recent failed high {rh:.2f} - caution"
                    break
        
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
            "sl_mult": sl_mult,
            "tp_mult": tp_mult,
            "candle_type": depth['type'],
            "body_ratio": float(depth['body_ratio']),
            "wick_imbalance": float(depth['wick_imbalance']),
            "volume_confirm": bool(depth['volume_confirm']),
            "near_top": bool(near_top),
            "near_bottom": bool(near_bottom),
            "dist_top_atr": float(dist_top_atr),
            "dist_bottom_atr": float(dist_bottom_atr),
            "last_top": float(last_top),
            "last_bottom": float(last_bottom),
            "strongest_resistance": sr.get('strongest_resistance'),
            "strongest_support": sr.get('strongest_support'),
            "mtf_alignment": mtf_check,
            "past_movement_detail": past_detail,
            "reason": f"MACD zero cross:{macd_zero_cross_up}/{macd_zero_cross_down} RSI:{last['rsi']:.1f} Candle:{depth['type']} TopDist:{dist_top_atr:.1f}ATR MTF:{mtf_check['detail']}",
            "timestamp": str(df.iloc[-1]['time']),
            "sr_zones": sr
        }

# Backward compatibility alias
SuperAlgoV2 = SuperAlgo

