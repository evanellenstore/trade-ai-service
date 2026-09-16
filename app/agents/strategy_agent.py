from app.models.trading_state import TradingState


DEFAULT_WEIGHTS = {"trend": 2, "supertrend": 2, "ema": 2, "macd": 2, "volume": 1}
MIN_RISK_REWARD = 1.5


def _direction(value: str | None) -> str:
    normalized = (value or "").upper()
    if normalized in {"BUY", "BULLISH", "UP"}:
        return "BUY"
    if normalized in {"SELL", "BEARISH", "DOWN"}:
        return "SELL"
    return "HOLD"


def _risk_reward(state: TradingState, signal: str) -> float | None:
    stop_loss, take_profit = state.stop_loss, state.take_profit
    if stop_loss is None or take_profit is None:
        if signal == "BUY":
            stop_loss, take_profit = state.support1, state.resistance1
        elif signal == "SELL":
            stop_loss, take_profit = state.resistance1, state.support1
    if signal == "BUY" and stop_loss is not None and take_profit is not None:
        risk, reward = state.price - stop_loss, take_profit - state.price
    elif signal == "SELL" and stop_loss is not None and take_profit is not None:
        risk, reward = stop_loss - state.price, state.price - take_profit
    else:
        return None
    return reward / risk if risk > 0 and reward > 0 else 0.0


def _timeframe_consensus(state: TradingState, signal: str) -> tuple[bool, dict[str, float]]:
    if not state.timeframe_analysis:
        return True, {"aligned": 1, "total": 1}
    votes = {"BUY": 0.0, "SELL": 0.0}
    for details in state.timeframe_analysis.values():
        if not isinstance(details, dict):
            continue
        direction = _direction(details.get("signal") or details.get("trend"))
        weight = max(float(details.get("weight", 1)), 0)
        if direction in votes:
            votes[direction] += weight
    total = votes["BUY"] + votes["SELL"]
    aligned = signal in votes and votes[signal] > 0 and votes[signal] >= total / 2 if total else False
    return aligned, {"buy": votes["BUY"], "sell": votes["SELL"], "total": total}


def strategy_agent(state: TradingState) -> dict[str, object]:
    
    print("\n================== STRATEGY AGENT INPUT ==================")
    print(state.model_dump_json(indent=2))
    print("=======================================================\n")

    weights = {**DEFAULT_WEIGHTS, **state.strategy_weights}
    bullish_score = 0.0
    bearish_score = 0.0

    signal = (state.signal or "HOLD").upper()
    trend = (state.trend or "SIDEWAYS").upper()
    if trend in {"UP", "BULLISH"}:
        trend = "BULLISH"
    elif trend in {"DOWN", "BEARISH"}:
        trend = "BEARISH"
    elif trend in {"SIDEWAYS", "NEUTRAL"}:
        trend = "SIDEWAYS"
    else:
        trend = "UNKNOWN"

    # Trend Alignment

    if signal == "BUY":

        if trend == "BULLISH":
            bullish_score += weights["trend"]

        elif trend == "BEARISH":
            bearish_score += weights["trend"]

    elif signal == "SELL":

        if trend == "BEARISH":
            bearish_score += weights["trend"]

        elif trend == "BULLISH":
            bullish_score += weights["trend"]

    # SuperTrend Confirmation

    supertrend = (state.supertrend_signal or "UNKNOWN").upper()
    if supertrend == "BUY":
        bullish_score += weights["supertrend"]
    elif supertrend == "SELL":
        bearish_score += weights["supertrend"]

    # EMA Confirmation

    bullish_ema = (
        state.ema20 is not None
        and state.ema50 is not None
        and state.ema20 > state.ema50
    )

    bearish_ema = (
        state.ema20 is not None
        and state.ema50 is not None
        and state.ema20 < state.ema50
    )

    if bullish_ema:
        bullish_score += weights["ema"]
    elif bearish_ema:
        bearish_score += weights["ema"]

    # MACD Confirmation

    if signal == "BUY" and (state.macd_histogram or 0) > 0:
        bullish_score += weights["macd"]

    if signal == "SELL" and (state.macd_histogram or 0) < 0:
        bearish_score += weights["macd"]

    # Volume Confirmation

    if state.volume_spike and signal in {"BUY", "SELL"}:
        if signal == "BUY":
            bullish_score += weights["volume"]
        else:
            bearish_score += weights["volume"]

    # ADX Confirmation

    trend_quality = "WEAK"

    if state.adx is not None:

        if state.adx >= 25:
            trend_quality = "STRONG"

        elif state.adx >= 20:
            trend_quality = "MODERATE"

    # Strategy Confidence Band

    confidence_band = "LOW"

    strategy_confidence = state.strategy_confidence or 0

    if strategy_confidence >= 80:
        confidence_band = "HIGH"

    elif strategy_confidence >= 60:
        confidence_band = "MEDIUM"

    # Final Validation Score

    validation_score = bullish_score - bearish_score
    supertrend_conflict = (
        signal in {"BUY", "SELL"}
        and supertrend in {"BUY", "SELL"}
        and supertrend != signal
    )

    if supertrend_conflict:
        validation_result = "CONFLICT"
    elif validation_score >= 3:
        validation_result = "STRONG_CONFIRMATION"

    elif validation_score >= 1:
        validation_result = "CONFIRMATION"

    elif validation_score == 0:
        validation_result = "NEUTRAL"

    else:
        validation_result = "CONFLICT"

    risk_reward = _risk_reward(state, signal)
    risk_reward_passed = risk_reward is None or risk_reward >= MIN_RISK_REWARD
    timeframe_passed, timeframe_votes = _timeframe_consensus(state, signal)
    volume_passed = signal not in {"BUY", "SELL"} or state.volume_spike
    approved = signal if risk_reward_passed and timeframe_passed and volume_passed else "HOLD"
    filter_result = "PASSED"
    if not risk_reward_passed:
        filter_result = "RISK_REWARD"
    elif not timeframe_passed:
        filter_result = "TIMEFRAME"
    elif not volume_passed:
        filter_result = "VOLUME"

    return {
        "strategy_analysis": {
            "strategy_name": state.strategy_name,
            "strategy_signal": signal,
            "strategy_confidence": strategy_confidence,
            "confidence_band": confidence_band,
            "market_regime": state.market_regime,
            "trend": trend,
            "trend_strength": state.trend_strength,
            "trend_quality": trend_quality,
            "supertrend": supertrend,
            "supertrend_conflict": supertrend_conflict,
            "validation_score": validation_score,
            "validation_result": validation_result,
            "raw_signal": signal,
            "approved_signal": approved,
            "phase1_filter": filter_result,
            "volume_confirmed": state.volume_spike,
            "risk_reward": risk_reward,
            "risk_reward_threshold": MIN_RISK_REWARD,
            "risk_reward_passed": risk_reward_passed,
            "timeframe_consensus": timeframe_passed,
            "timeframe_votes": timeframe_votes,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score
        }
    }