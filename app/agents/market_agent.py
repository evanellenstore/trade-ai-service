from app.models.trading_state import TradingState


def market_agent(state: TradingState) -> dict[str, object]:

    print("\n================== MARKET AGENT INPUT ==================")
    print(state.model_dump_json(indent=2))
    print("=======================================================\n")
    
    
    bullish_score = 0
    bearish_score = 0

    # --------------------------------------------------
    # Trend Analysis
    # --------------------------------------------------

    trend = (state.trend or "UNKNOWN").upper()

    if trend == "UP":
        bullish_score += 3
    elif trend == "DOWN":
        bearish_score += 3

    # --------------------------------------------------
    # Trend Strength
    # --------------------------------------------------

    trend_strength = (state.trend_strength or "UNKNOWN").upper()

    if trend_strength == "STRONG":
        if trend == "UP":
            bullish_score += 2
        elif trend == "DOWN":
            bearish_score += 2

    # --------------------------------------------------
    # Market Regime
    # --------------------------------------------------

    market_regime = (state.market_regime or "UNKNOWN").upper()

    if market_regime == "TRENDING":
        if trend == "UP":
            bullish_score += 1
        elif trend == "DOWN":
            bearish_score += 1

    # --------------------------------------------------
    # VWAP Analysis
    # --------------------------------------------------

    vwap_position = "UNKNOWN"

    if state.vwap is not None:

        if state.price >= state.vwap:
            vwap_position = "ABOVE_VWAP"
            bullish_score += 1
        else:
            vwap_position = "BELOW_VWAP"
            bearish_score += 1

    # --------------------------------------------------
    # ATR Volatility
    # --------------------------------------------------

    if state.atr is None:
        volatility = "UNKNOWN"
    elif state.atr >= 20:
        volatility = "HIGH"
    elif state.atr >= 10:
        volatility = "MEDIUM"
    else:
        volatility = "LOW"

    # --------------------------------------------------
    # Support / Resistance Distance
    # --------------------------------------------------

    market_zone = "NEUTRAL"

    support_distance = None
    resistance_distance = None

    if (
        state.support1 is not None
        and state.resistance1 is not None
    ):

        support_distance = round(
            abs(state.price - state.support1),
            2
        )

        resistance_distance = round(
            abs(state.resistance1 - state.price),
            2
        )

        if support_distance < resistance_distance:
            market_zone = "NEAR_SUPPORT"
            bullish_score += 1

        elif resistance_distance < support_distance:
            market_zone = "NEAR_RESISTANCE"
            bearish_score += 1

    # --------------------------------------------------
    # Market Bias
    # --------------------------------------------------

    score_diff = bullish_score - bearish_score

    if score_diff >= 3:
        market_bias = "BULLISH"

    elif score_diff <= -3:
        market_bias = "BEARISH"

    else:
        market_bias = "NEUTRAL"

    return {
        "market_analysis": {
            "symbol": state.symbol,
            "price": state.price,

            "trend": trend,
            "trend_strength": trend_strength,
            "market_regime": market_regime,

            "vwap_position": vwap_position,
            "volatility": volatility,

            "support": state.support1,
            "resistance": state.resistance1,

            "support_distance": support_distance,
            "resistance_distance": resistance_distance,

            "market_zone": market_zone,

            "bullish_score": bullish_score,
            "bearish_score": bearish_score,

            "market_bias": market_bias
        }
    }