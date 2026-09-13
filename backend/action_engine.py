"""
Action Engine V2 - Core Upgrade
Handles depth analysis before trade, approval vs auto-approved, demo vs real safety
Integrates all subagents knowledge: depth analysis, strategies review, pattern analysis, trade movement, direction, past movement, historical top/high resistant
"""
from datetime import datetime
import json, os, uuid
from enum import Enum

class ActionMode(Enum):
    MANUAL_APPROVAL = "manual"  # All need approval
    AUTO_DEMO = "auto_demo"  # Demo auto-approved >=70
    AUTO_REAL_STRICT = "auto_real_strict"  # Real score>=85 + all depth pass + beyond 10 trades

class ActionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    BLOCKED_RISK = "blocked_risk"

class ActionEngine:
    def __init__(self, config, risk_manager, alert_manager):
        self.config = config
        self.risk_manager = risk_manager
        self.alert_manager = alert_manager
        self.pending_actions = {}  # ticket -> action dict
        self.action_history = []
        self.auto_approval_threshold = 85
        self.demo_threshold = 70
        self.bot_mode = "full_auto" if getattr(config, 'AUTO_TRADING', False) else "semi_auto"
        self.max_positions = 3
        os.makedirs("logs", exist_ok=True)

    def set_bot_mode(self, mode: str):
        if mode in ["manual", "semi_auto", "full_auto"]:
            self.bot_mode = mode
            self.log(f"Bot trading mode switched to: {mode.upper()}")
            return True
        return False

    def compute_multi_strategy_composite_score(self, signal_data, mtf_data, historical_data):
        """
        Single Base Auto Trader Engine:
        Computes 5 individual strategy sub-scores (0-100) and unifies into a single Composite Score (0-100):
        1. Trend Pullback (25%)
        2. Mean Reversion 25% Gate (20%)
        3. Volatility & Breakout (15%)
        4. Candlestick & Pattern Depth (20%)
        5. MTF Alignment Matrix (20%)
        """
        sig_type = signal_data.get('signal', 'NEUTRAL')
        is_bull = sig_type.startswith('LE')
        is_bear = sig_type.startswith('SE')
        rsi = signal_data.get('rsi', 50)
        macd = signal_data.get('macd', signal_data.get('macd_line', 0))
        atr = signal_data.get('atr', 1)
        depth_type = signal_data.get('candle_type', 'normal')
        body_ratio = signal_data.get('body_ratio', 0.5)

        # 1. Trend Pullback Strategy (EMA alignment + healthy pullback)
        trend_score = 50
        if is_bull:
            if 48 <= rsi <= 68: trend_score += 25
            if macd > 0: trend_score += 15
            if depth_type in ['hammer', 'strong_bull', 'bullish_engulfing']: trend_score += 10
        elif is_bear:
            if 32 <= rsi <= 52: trend_score += 25
            if macd < 0: trend_score += 15
            if depth_type in ['gravestone', 'strong_bear']: trend_score += 10
        trend_score = max(0, min(100, trend_score))

        # 2. Mean Reversion Strategy (25% Gate - BB extreme + RSI exhaustion)
        reversion_score = 45
        dist_top = signal_data.get('dist_top_atr', 2.0)
        dist_bottom = signal_data.get('dist_bottom_atr', 2.0)
        if is_bull and dist_bottom < 1.0: reversion_score += 35
        if is_bear and dist_top < 1.0: reversion_score += 35
        if is_bull and rsi < 42: reversion_score += 20
        if is_bear and rsi > 58: reversion_score += 20
        reversion_score = max(0, min(100, reversion_score))

        # 3. Volatility & Breakout Strategy (ATR surge + volume)
        breakout_score = 50
        if signal_data.get('volume_confirm'): breakout_score += 30
        if atr > 0 and body_ratio > 0.6: breakout_score += 20
        breakout_score = max(0, min(100, breakout_score))

        # 4. Candlestick & Pattern Depth Strategy
        pattern_score = 50
        if depth_type in ['hammer', 'strong_bull'] and is_bull: pattern_score = 85
        elif depth_type in ['gravestone', 'strong_bear'] and is_bear: pattern_score = 85
        elif depth_type == 'bullish_engulfing' and is_bull: pattern_score = 80
        elif depth_type == 'doji': pattern_score = 30
        pattern_score = max(0, min(100, pattern_score))

        # 5. MTF Alignment Matrix Strategy
        mtf_score = 50
        mtf_bull = 0
        mtf_bear = 0
        if mtf_data:
            for tf, s in mtf_data.items():
                if s and (s.get('signal') or '').startswith('LE'): mtf_bull += 1
                elif s and (s.get('signal') or '').startswith('SE'): mtf_bear += 1
            if is_bull:
                mtf_score = int((mtf_bull / max(1, len(mtf_data))) * 100)
            elif is_bear:
                mtf_score = int((mtf_bear / max(1, len(mtf_data))) * 100)
        mtf_score = max(0, min(100, mtf_score))

        # Composite Unified Score
        composite_score = (
            trend_score * 0.25 +
            reversion_score * 0.20 +
            breakout_score * 0.15 +
            pattern_score * 0.20 +
            mtf_score * 0.20
        )
        base_score = signal_data.get('score', 50)
        final_composite = round((composite_score * 0.7) + (base_score * 0.3), 1)
        final_composite = max(0, min(100, final_composite))

        return {
            "composite_score": final_composite,
            "strategies": {
                "trend_pullback": trend_score,
                "mean_reversion": reversion_score,
                "volatility_breakout": breakout_score,
                "pattern_depth": pattern_score,
                "mtf_alignment": mtf_score
            }
        }

    def depth_analysis_before_trade(self, symbol, timeframe, signal_data, mtf_data, historical_data):
        """
        Very depth analysis before every trade - as requested
        Returns detailed analysis dict with scores
        """
        analysis = {
            "timestamp": str(datetime.now()),
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal_data,
            "checks": {},
            "overall_score": 0,
            "can_trade": False,
            "reason": "",
            "action_required": "approval"  # or auto_approved
        }

        # 1. Candle Depth Analysis
        depth = signal_data.get('candle_type', 'normal')
        body_ratio = signal_data.get('body_ratio', 0)
        depth_score = 0
        if depth in ['hammer', 'strong_bull'] and signal_data['signal'].startswith('LE'):
            depth_score = 15
        elif depth in ['gravestone', 'strong_bear'] and signal_data['signal'].startswith('SE'):
            depth_score = 15
        elif depth == 'doji':
            depth_score = -10  # indecision, avoid
        else:
            depth_score = 5
        analysis["checks"]["candle_depth"] = {
            "type": depth,
            "body_ratio": body_ratio,
            "score": depth_score,
            "detail": f"Candle {depth} body {body_ratio:.2f} {'bullish' if body_ratio>0.7 else 'indecision' if body_ratio<0.3 else 'normal'}"
        }

        # 2. Trade Movement and Direction Analysis
        movement = "strong_bullish" if signal_data.get('rsi', 50) > 60 and signal_data.get('macd', 0) > 0 else "weak" if signal_data.get('rsi', 50) > 50 else "bearish"
        direction = "bullish" if signal_data['signal'].startswith('LE') else "bearish" if signal_data['signal'].startswith('SE') else "neutral"
        direction_score = 10 if (movement == "strong_bullish" and direction == "bullish") or (movement == "bearish" and direction == "bearish") else 0
        analysis["checks"]["trade_movement"] = {
            "movement": movement,
            "direction": direction,
            "score": direction_score,
            "detail": f"Movement {movement}, direction {direction}, RSI {signal_data.get('rsi',0):.1f}, MACD {signal_data.get('macd',0):.2f}"
        }

        # 3. Past Trade Movement Base Analysis (compare to last 50)
        past_analysis_score = 0
        past_detail = "No repeating failed breakout detected"
        if historical_data is not None and len(historical_data) > 50:
            recent = historical_data.tail(50)
            # Check if current price near recent failed breakout level
            recent_highs = recent['high'].nlargest(5)
            current_price = signal_data.get('price', 0)
            for rh in recent_highs:
                if abs(current_price - rh) / current_price < 0.002:  # within 0.2%
                    past_analysis_score = -10
                    past_detail = f"Current price near recent failed breakout high {rh:.2f} - caution"
                    break
            else:
                past_analysis_score = 10
                past_detail = "Past 50 candles no repeating failed pattern, clear"
        analysis["checks"]["past_movement"] = {
            "score": past_analysis_score,
            "detail": past_detail
        }

        # 4. Historical Closed Top and High Resistant Base Analysis
        top_score = 0
        last_top = signal_data.get('last_top', 0)
        last_bottom = signal_data.get('last_bottom', 0)
        dist_top = signal_data.get('dist_top', 999) if 'dist_top' in signal_data else 999
        dist_bottom = signal_data.get('dist_bottom', 999) if 'dist_bottom' in signal_data else 999
        # Actually calculate from signal_data if not present
        atr = signal_data.get('atr', 1)
        price = signal_data.get('price', 0)
        if last_top and atr:
            dist_top = abs(price - last_top) / atr
        if last_bottom and atr:
            dist_bottom = abs(price - last_bottom) / atr

        near_top = dist_top < 0.8  # adaptive: XAU ATR $2-5, BTC ATR $150-300, 0.8 ATR = close
        near_bottom = dist_bottom < 0.8

        # Check rejection count (simulate from historical_data)
        rejection_count = 0
        if historical_data is not None and len(historical_data) > 100:
            recent_100 = historical_data.tail(100)
            for _, row in recent_100.iterrows():
                if abs(row['high'] - last_top) / last_top < 0.001 if last_top else False:
                    rejection_count += 1

        if near_top and signal_data['signal'].startswith('LE'):
            top_score = -15  # avoid long near top
            detail = f"Near last top {last_top:.2f} dist {dist_top:.2f} ATR rejection count {rejection_count} - HIGH RISK double top"
        elif near_bottom and signal_data['signal'].startswith('SE'):
            top_score = -15
            detail = f"Near last bottom {last_bottom:.2f} dist {dist_bottom:.2f} ATR - avoid short at bottom"
        elif near_top and signal_data['signal'].startswith('SE'):
            top_score = 15
            detail = f"Near top {last_top:.2f} good for short, rejection {rejection_count}"
        elif near_bottom and signal_data['signal'].startswith('LE'):
            top_score = 15
            detail = f"Near bottom {last_bottom:.2f} good for long, support held"
        else:
            top_score = 5
            detail = f"Mid range, dist top {dist_top:.2f} ATR bottom {dist_bottom:.2f} ATR safe"

        analysis["checks"]["historical_top_resistant"] = {
            "last_top": last_top,
            "last_bottom": last_bottom,
            "dist_top_atr": dist_top,
            "dist_bottom_atr": dist_bottom,
            "rejection_count": rejection_count,
            "near_top": near_top,
            "near_bottom": near_bottom,
            "score": top_score,
            "detail": detail
        }

        # 5. Strategies Review Scoring
        strategy_score = 0
        strategy_details = []
        # Trend Pullback: EMA alignment + price near EMA + RSI + bull candle
        ema_bull = signal_data.get('ema_bull', True)  # from signal_data or mtf_data
        # Simplified scoring from mtf_data
        mtf_bullish_count = 0
        if mtf_data:
            for tf, sig in mtf_data.items():
                if sig and sig.get('signal', '').startswith('LE'):
                    mtf_bullish_count += 1
        if mtf_bullish_count >= 3:
            strategy_score += 10
            strategy_details.append(f"Trend Pullback MTF bullish {mtf_bullish_count}/4")
        else:
            strategy_details.append(f"Trend Pullback MTF weak {mtf_bullish_count}/4")

        # Mean reversion and breakout would be here
        analysis["checks"]["strategies_review"] = {
            "score": strategy_score,
            "details": strategy_details,
            "mtf_alignment": mtf_bullish_count
        }

        # 6. Pattern Analysis
        pattern_score = 0
        patterns_found = []
        if depth == 'hammer':
            pattern_score += 10
            patterns_found.append("Hammer at support")
        if depth == 'strong_bull' and signal_data.get('body_ratio',0) > 0.7:
            pattern_score += 8
            patterns_found.append("Strong bullish engulfing")
        # Add more pattern logic
        analysis["checks"]["pattern_analysis"] = {
            "score": pattern_score,
            "patterns": patterns_found,
            "detail": f"Patterns: {', '.join(patterns_found) if patterns_found else 'None strong'}"
        }

        # Multi-Strategy Combination Scoring (Single Base Auto Trader Engine)
        strat_calc = self.compute_multi_strategy_composite_score(signal_data, mtf_data, historical_data)
        analysis["strategy_breakdown"] = strat_calc["strategies"]
        composite_score = strat_calc["composite_score"]
        analysis["overall_score"] = composite_score

        # Can trade logic
        can_trade = True
        reasons_block = []
        if analysis["overall_score"] < 60:
            can_trade = False
            reasons_block.append(f"Composite score low {analysis['overall_score']:.1f} < 60")
        if near_top and signal_data['signal'].startswith('LE') and rejection_count >= 3:
            can_trade = False
            reasons_block.append(f"Double top risk: near top with {rejection_count} rejections")
        if depth == 'doji' and body_ratio < 0.2:
            can_trade = False
            reasons_block.append("Doji indecision, avoid")
        if past_analysis_score < 0:
            can_trade = False
            reasons_block.append(past_detail)

        analysis["can_trade"] = can_trade
        analysis["block_reasons"] = reasons_block

        # Action required logic based on bot_mode
        if not can_trade:
            analysis["action_required"] = "blocked"
            analysis["reason"] = "; ".join(reasons_block)
        elif self.bot_mode == "manual":
            analysis["action_required"] = "approval"
            analysis["reason"] = f"Manual Mode - User approval required | Score {analysis['overall_score']:.1f}"
        elif self.bot_mode == "semi_auto":
            analysis["action_required"] = "approval"
            analysis["reason"] = f"Semi-Auto Queue - Ready for approval | Score {analysis['overall_score']:.1f}"
        elif self.config.LIVE_TRADING:
            # Real account strict
            if self.risk_manager.real_trades_confirmed < 10:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Real first 10 trades require approval ({self.risk_manager.real_trades_confirmed}/10) + score {analysis['overall_score']:.1f}"
            elif analysis["overall_score"] >= self.auto_approval_threshold and top_score >= 0 and depth_score >= 0:
                analysis["action_required"] = "auto_approved"
                analysis["reason"] = f"Auto Bot Real: Score {analysis['overall_score']:.1f} >= {self.auto_approval_threshold} & depth passed"
            else:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Score {analysis['overall_score']:.1f} < {self.auto_approval_threshold} - queued for approval"
        else:
            # Demo Full Auto Bot
            if analysis["overall_score"] >= self.demo_threshold:
                analysis["action_required"] = "auto_approved"
                analysis["reason"] = f"Auto Bot Demo: Score {analysis['overall_score']:.1f} >= {self.demo_threshold} auto-executed"
            else:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Score {analysis['overall_score']:.1f} < {self.demo_threshold} queued for approval"

        return analysis

    def create_action(self, symbol, timeframe, signal_data, mtf_data=None, historical_data=None, equity=None):
        """Create pending action with depth analysis"""
        analysis = self.depth_analysis_before_trade(symbol, timeframe, signal_data, mtf_data, historical_data)
        
        # Risk check - only if real equity is passed (callers in main_v2 pass equity before execution).
        # NOTE: previously passed price as equity which falsely triggered daily-loss block (e.g. XAU 4313 vs 10k balance).
        if equity is not None:
            can_risk, risk_reason = self.risk_manager.check_daily_loss(equity)
            if not can_risk:
                analysis["can_trade"] = False
                analysis["action_required"] = "blocked_risk"
                analysis["reason"] += f" | Risk blocked: {risk_reason}"

        action_id = str(uuid.uuid4())[:8]
        action = {
            "id": action_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal_data.get('signal'),
            "price": signal_data.get('price'),
            "sl": signal_data.get('sl'),
            "tp": signal_data.get('tp'),
            "score": analysis["overall_score"],
            "base_score": signal_data.get('score'),
            "analysis": analysis,
            "status": ActionStatus.PENDING.value if analysis["action_required"]=="approval" else ActionStatus.AUTO_APPROVED.value if analysis["action_required"]=="auto_approved" else ActionStatus.BLOCKED_RISK.value if analysis["action_required"]=="blocked_risk" else ActionStatus.BLOCKED.value,
            "created": str(datetime.now()),
            "approval_required": analysis["action_required"]=="approval"
        }

        if action["status"] == ActionStatus.PENDING.value:
            self.pending_actions[action_id] = action
            # Send alert for approval
            self.alert_manager.create_alert(f"{symbol}-{timeframe} PENDING APPROVAL", signal_data)
            self.log(f"Action {action_id} PENDING approval - {symbol} {signal_data.get('signal')} score {analysis['overall_score']:.1f}")

        elif action["status"] == ActionStatus.AUTO_APPROVED.value:
            self.action_history.append(action)
            self.log(f"Action {action_id} AUTO-APPROVED - {symbol} {signal_data.get('signal')} score {analysis['overall_score']:.1f} - {analysis['reason']}")

        else:
            self.action_history.append(action)
            self.log(f"Action {action_id} BLOCKED - {analysis['reason']}")

        return action

    def approve_action(self, action_id):
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            action["status"] = ActionStatus.APPROVED.value
            action["approved_at"] = str(datetime.now())
            self.action_history.append(action)
            self.log(f"Action {action_id} APPROVED by user")
            return action
        return None

    def reject_action(self, action_id):
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            action["status"] = ActionStatus.REJECTED.value
            self.action_history.append(action)
            self.log(f"Action {action_id} REJECTED by user")
            return action
        return None

    def get_pending(self):
        return list(self.pending_actions.values())

    def get_history(self, limit=50):
        return self.action_history[-limit:][::-1]

    def manage_open_positions(self, trader):
        """
        Autonomous Trade Lifecycle Manager:
        - Break-Even (BE) Shift: when profit reaches +1.2R or +1.2 ATR, move SL to Entry + buffer.
        - Trailing Stop: when profit reaches +2.0R, trail SL along ATR to lock in gains.
        - Returns list of management events triggered.
        """
        positions = trader.get_positions()
        events = []
        for p in positions:
            ticket = p.get("ticket")
            symbol = p.get("symbol", "")
            ptype = p.get("type", "BUY")
            open_price = float(p.get("price_open") or 0)
            curr_price = float(p.get("price_current") or open_price)
            sl = float(p.get("sl") or 0)
            tp = float(p.get("tp") or 0)
            if open_price == 0 or ticket is None:
                continue

            # Adaptive ATR approximation per symbol
            atr_est = open_price * (0.003 if "XAU" in symbol else 0.006)
            risk = abs(open_price - sl) if sl > 0 else (atr_est * 1.5)

            if ptype == "BUY":
                gain = curr_price - open_price
                r_multiple = gain / risk if risk > 0 else 0
                
                # 1. Break-Even Check (+1.2R or +1.2 ATR)
                if (r_multiple >= 1.2 or gain >= atr_est * 1.2) and (sl < open_price or sl == 0):
                    new_sl = round(open_price + (atr_est * 0.1), 2)
                    trader.modify_position(ticket, new_sl, tp)
                    msg = f"Ticket #{ticket} ({symbol} BUY): Auto shifted to BREAK-EVEN (SL: {new_sl})"
                    self.log(msg)
                    events.append({"type": "break_even", "ticket": ticket, "symbol": symbol, "new_sl": new_sl, "message": msg})
                
                # 2. Trailing Stop Check (+2.0R)
                elif r_multiple >= 2.0 and (curr_price - (atr_est * 1.2)) > sl:
                    new_sl = round(curr_price - (atr_est * 1.2), 2)
                    trader.modify_position(ticket, new_sl, tp)
                    msg = f"Ticket #{ticket} ({symbol} BUY): TRAILING STOP updated to {new_sl}"
                    self.log(msg)
                    events.append({"type": "trailing_stop", "ticket": ticket, "symbol": symbol, "new_sl": new_sl, "message": msg})

            elif ptype == "SELL":
                gain = open_price - curr_price
                r_multiple = gain / risk if risk > 0 else 0
                
                # 1. Break-Even Check
                if (r_multiple >= 1.2 or gain >= atr_est * 1.2) and (sl > open_price or sl == 0):
                    new_sl = round(open_price - (atr_est * 0.1), 2)
                    trader.modify_position(ticket, new_sl, tp)
                    msg = f"Ticket #{ticket} ({symbol} SELL): Auto shifted to BREAK-EVEN (SL: {new_sl})"
                    self.log(msg)
                    events.append({"type": "break_even", "ticket": ticket, "symbol": symbol, "new_sl": new_sl, "message": msg})
                
                # 2. Trailing Stop Check
                elif r_multiple >= 2.0 and (curr_price + (atr_est * 1.2)) < sl:
                    new_sl = round(curr_price + (atr_est * 1.2), 2)
                    trader.modify_position(ticket, new_sl, tp)
                    msg = f"Ticket #{ticket} ({symbol} SELL): TRAILING STOP updated to {new_sl}"
                    self.log(msg)
                    events.append({"type": "trailing_stop", "ticket": ticket, "symbol": symbol, "new_sl": new_sl, "message": msg})

        return events

    def log(self, msg):
        entry = f"[{datetime.now()}] [ACTION_ENGINE] {msg}"
        print(entry)
        try:
            with open("logs/action_engine.log", "a") as f:
                f.write(entry+"\n")
        except:
            pass
