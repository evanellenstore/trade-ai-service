from app.models.trading_state import TradingState


def technical_agent(state: TradingState) -> dict[str, object]:
    
    print("\n================== TECHNICAL AGENT INPUT ==================")
    print(state.model_dump_json(indent=2))
    print("=======================================================\n")

    bullish_score = 0
    bearish_score = 0

    signals = {}

    # ==========================================================
    # EMA ANALYSIS
    # ==========================================================

    ema_signal = "NEUTRAL"

    if all([
        state.ema20,
        state.ema50,
        state.ema100,
        state.ema200
    ]):

        if (
            state.ema20 > state.ema50 >
            state.ema100 > state.ema200
        ):
            ema_signal = "STRONG_BULLISH"
            bullish_score += 3

        elif (
            state.ema20 < state.ema50 <
            state.ema100 < state.ema200
        ):
            ema_signal = "STRONG_BEARISH"
            bearish_score += 3

        elif state.ema20 > state.ema50:
            ema_signal = "BULLISH"
            bullish_score += 2

        elif state.ema20 < state.ema50:
            ema_signal = "BEARISH"
            bearish_score += 2

    signals["ema"] = ema_signal

    # ==========================================================
    # RSI ANALYSIS
    # ==========================================================

    rsi_signal = "UNKNOWN"

    if state.rsi14 and state.rsi14 > 0:

        if state.rsi14 <= 30:
            rsi_signal = "OVERSOLD"
            bullish_score += 1

        elif state.rsi14 >= 70:
            rsi_signal = "OVERBOUGHT"
            bearish_score += 1

        else:
            rsi_signal = "NEUTRAL"

    signals["rsi"] = rsi_signal

    # ==========================================================
    # MACD ANALYSIS
    # ==========================================================

    macd_signal = "NEUTRAL"

    if state.macd_histogram is not None:

        if state.macd_histogram > 0:
            macd_signal = "BULLISH"
            bullish_score += 2

        elif state.macd_histogram < 0:
            macd_signal = "BEARISH"
            bearish_score += 2

    signals["macd"] = macd_signal

    # ==========================================================
    # ADX ANALYSIS
    # ==========================================================

    adx_signal = "UNKNOWN"

    if state.adx and state.adx > 0:

        if state.adx >= 40:
            adx_signal = "VERY_STRONG"

        elif state.adx >= 25:
            adx_signal = "STRONG"

        elif state.adx >= 20:
            adx_signal = "MODERATE"

        else:
            adx_signal = "WEAK"

    signals["adx"] = adx_signal

    # ==========================================================
    # ATR ANALYSIS
    # ==========================================================

    atr_signal = "UNKNOWN"

    if state.atr is not None:

        if state.atr >= 30:
            atr_signal = "HIGH_VOLATILITY"

        elif state.atr >= 15:
            atr_signal = "MEDIUM_VOLATILITY"

        else:
            atr_signal = "LOW_VOLATILITY"

    signals["atr"] = atr_signal

    # ==========================================================
    # VWAP ANALYSIS
    # ==========================================================

    vwap_signal = "UNKNOWN"

    if state.vwap is not None:

        if state.price > state.vwap:
            vwap_signal = "ABOVE_VWAP"
            bullish_score += 1

        else:
            vwap_signal = "BELOW_VWAP"
            bearish_score += 1

    signals["vwap"] = vwap_signal

    # ==========================================================
    # SUPERTREND ANALYSIS
    # ==========================================================

    supertrend = state.supertrend_signal or "UNKNOWN"

    if supertrend == "BUY":
        bullish_score += 3

    elif supertrend == "SELL":
        bearish_score += 3

    signals["supertrend"] = supertrend

    # ==========================================================
    # VOLUME ANALYSIS
    # ==========================================================

    volume_signal = "NORMAL"

    if state.volume_spike:

        volume_signal = "SPIKE"

        if bullish_score >= bearish_score:
            bullish_score += 1
        else:
            bearish_score += 1

    signals["volume"] = volume_signal

    # ==========================================================
    # PATTERN ANALYSIS
    # ==========================================================

    bullish_patterns = {
        "HAMMER",
        "MORNING_STAR",
        "BULLISH_ENGULFING",
        "PIERCING"
    }

    bearish_patterns = {
        "SHOOTING_STAR",
        "EVENING_STAR",
        "BEARISH_ENGULFING"
    }

    pattern_signal = state.pattern or "NONE"

    if pattern_signal in bullish_patterns:
        bullish_score += 2

    if pattern_signal in bearish_patterns:
        bearish_score += 2

    signals["pattern"] = pattern_signal

    # ==========================================================
    # SUPPORT / RESISTANCE
    # ==========================================================

    price_position = "NEUTRAL"

    if state.support1 and state.resistance1:

        support_distance = abs(state.price - state.support1)
        resistance_distance = abs(state.resistance1 - state.price)

        if support_distance < resistance_distance:
            price_position = "NEAR_SUPPORT"
            bullish_score += 1

        elif resistance_distance < support_distance:
            price_position = "NEAR_RESISTANCE"
            bearish_score += 1

    signals["price_position"] = price_position

    # ==========================================================
    # OVERALL TECHNICAL SIGNAL
    # ==========================================================

    difference = bullish_score - bearish_score

    if difference >= 4:
        technical_signal = "STRONG_BUY"

    elif difference >= 2:
        technical_signal = "BUY"

    elif difference <= -4:
        technical_signal = "STRONG_SELL"

    elif difference <= -2:
        technical_signal = "SELL"

    else:
        technical_signal = "NEUTRAL"

    return {
        "technical_analysis": {
            "technical_signal": technical_signal,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "score_difference": difference,
            "signals": signals
        }
    }