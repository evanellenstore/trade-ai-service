from app.models.trading_state import TradingState


def strategy_agent(state: TradingState) -> dict[str, object]:
    
    print("\n================== STRATEGY AGENT INPUT ==================")
    print(state.model_dump_json(indent=2))
    print("=======================================================\n")

    bullish_score = 0
    bearish_score = 0

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
            bullish_score += 2

        elif trend == "BEARISH":
            bearish_score += 2

    elif signal == "SELL":

        if trend == "BEARISH":
            bearish_score += 2

        elif trend == "BULLISH":
            bullish_score += 2

    # SuperTrend Confirmation

    supertrend = (state.supertrend_signal or "UNKNOWN").upper()
    if supertrend == "BUY":
        bullish_score += 2
    elif supertrend == "SELL":
        bearish_score += 2

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
        bullish_score += 2
    elif bearish_ema:
        bearish_score += 2

    # MACD Confirmation

    if signal == "BUY" and (state.macd_histogram or 0) > 0:
        bullish_score += 2

    if signal == "SELL" and (state.macd_histogram or 0) < 0:
        bearish_score += 2

    # Volume Confirmation

    if state.volume_spike and signal in {"BUY", "SELL"}:
        if signal == "BUY":
            bullish_score += 1
        else:
            bearish_score += 1

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
            "bullish_score": bullish_score,
            "bearish_score": bearish_score
        }
    }