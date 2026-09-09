from app.models.trading_state import TradingState


SUPERTREND_WEIGHT = 3
EMA_WEIGHT = 2
MACD_WEIGHT = 2
PATTERN_WEIGHT = 2
VWAP_WEIGHT = 1
RSI_WEIGHT = 1
VOLUME_WEIGHT = 1


def technical_agent(state: TradingState) -> dict[str, object]:

    bullish_score = 0
    bearish_score = 0

    # EMA

    ema_signal = "NEUTRAL"

    if all(
        value is not None
        for value in [
            state.ema20,
            state.ema50,
            state.ema100,
            state.ema200,
        ]
    ):

        if (
            state.ema20 > state.ema50 >
            state.ema100 > state.ema200
        ):
            ema_signal = "STRONG_BULLISH"
            bullish_score += EMA_WEIGHT

        elif (
            state.ema20 < state.ema50 <
            state.ema100 < state.ema200
        ):
            ema_signal = "STRONG_BEARISH"
            bearish_score += EMA_WEIGHT

        elif state.ema20 > state.ema50:
            ema_signal = "BULLISH"
            bullish_score += EMA_WEIGHT

        elif state.ema20 < state.ema50:
            ema_signal = "BEARISH"
            bearish_score += EMA_WEIGHT

    # RSI

    rsi_state = "UNKNOWN"

    if state.rsi14 and state.rsi14 > 0:

        if state.rsi14 <= 30:
            rsi_state = "OVERSOLD"
            bullish_score += RSI_WEIGHT

        elif state.rsi14 >= 70:
            rsi_state = "OVERBOUGHT"
            bearish_score += RSI_WEIGHT

        else:
            rsi_state = "NEUTRAL"

    # MACD

    macd_signal = "NEUTRAL"

    if state.macd_histogram is not None:

        if state.macd_histogram > 0:
            macd_signal = "BULLISH"
            bullish_score += MACD_WEIGHT

        elif state.macd_histogram < 0:
            macd_signal = "BEARISH"
            bearish_score += MACD_WEIGHT

    # ADX

    adx_state = "UNKNOWN"

    if state.adx and state.adx > 0:

        if state.adx >= 25:
            adx_state = "STRONG"

        elif state.adx >= 20:
            adx_state = "MODERATE"

        else:
            adx_state = "WEAK"

    # VWAP

    vwap_signal = "UNKNOWN"

    if state.vwap is not None:

        if state.price > state.vwap:
            vwap_signal = "ABOVE"
            bullish_score += VWAP_WEIGHT
        else:
            vwap_signal = "BELOW"
            bearish_score += VWAP_WEIGHT

    # SuperTrend

    supertrend_signal = state.supertrend_signal or "UNKNOWN"

    if supertrend_signal == "BUY":
        bullish_score += SUPERTREND_WEIGHT

    elif supertrend_signal == "SELL":
        bearish_score += SUPERTREND_WEIGHT

    # Candlestick Patterns

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

    if state.pattern in bullish_patterns:
        bullish_score += PATTERN_WEIGHT

    if state.pattern in bearish_patterns:
        bearish_score += PATTERN_WEIGHT

    # Volume Spike

    if state.volume_spike:

        if bullish_score >= bearish_score:
            bullish_score += VOLUME_WEIGHT
        else:
            bearish_score += VOLUME_WEIGHT

    return {
        "technical_analysis": {
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "signals": {
                "ema": ema_signal,
                "rsi": rsi_state,
                "macd": macd_signal,
                "adx": adx_state,
                "vwap": vwap_signal,
                "supertrend": supertrend_signal,
                "pattern": state.pattern,
                "volume_spike": state.volume_spike
            }
        }
    }
