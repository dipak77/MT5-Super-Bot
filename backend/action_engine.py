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
        os.makedirs("logs", exist_ok=True)

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

        # Overall score calculation (weights from subagents)
        overall = (
            depth_score * 0.15 +
            direction_score * 0.10 +
            past_analysis_score * 0.10 +
            top_score * 0.20 +
            strategy_score * 0.15 +
            pattern_score * 0.15 +
            signal_data.get('score',0) * 0.15  # base signal score
        )
        analysis["overall_score"] = max(0, min(100, overall + 50))  # normalize to 0-100
        # Adjust to be more realistic: if base signal 70, overall should be around 70
        analysis["overall_score"] = (analysis["overall_score"] + signal_data.get('score',0)) / 2

        # Can trade logic
        can_trade = True
        reasons_block = []
        if analysis["overall_score"] < 60:
            can_trade = False
            reasons_block.append(f"Overall score low {analysis['overall_score']:.1f} <60")
        if near_top and signal_data['signal'].startswith('LE') and rejection_count >=3:
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

        # Action required logic
        if not can_trade:
            analysis["action_required"] = "blocked"
            analysis["reason"] = "; ".join(reasons_block)
        elif self.config.LIVE_TRADING:
            # Real account strict
            if self.risk_manager.real_trades_confirmed < 10:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Real first 10 trades require approval ({self.risk_manager.real_trades_confirmed}/10) + score {analysis['overall_score']:.1f}"
            elif analysis["overall_score"] >= self.auto_approval_threshold and top_score >=0 and depth_score >=0:
                analysis["action_required"] = "auto_approved"
                analysis["reason"] = f"Score {analysis['overall_score']:.1f} >= {self.auto_approval_threshold} and all depth pass - auto approved real"
            else:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Score {analysis['overall_score']:.1f} < {self.auto_approval_threshold} or depth fail - need approval"
        else:
            # Demo
            if analysis["overall_score"] >= self.demo_threshold:
                analysis["action_required"] = "auto_approved"
                analysis["reason"] = f"Demo score {analysis['overall_score']:.1f} >= {self.demo_threshold} auto approved"
            else:
                analysis["action_required"] = "approval"
                analysis["reason"] = f"Demo score {analysis['overall_score']:.1f} < {self.demo_threshold} need approval"

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

    def log(self, msg):
        entry = f"[{datetime.now()}] [ACTION_ENGINE] {msg}"
        print(entry)
        try:
            with open("logs/action_engine.log", "a") as f:
                f.write(entry+"\n")
        except:
            pass
