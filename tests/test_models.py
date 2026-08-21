def test_events_build_unified_state(signal, snapshot):
    from app.models.trading_state import TradingState

    state = TradingState.from_events(signal, snapshot)

    assert state.signal_id == "SIG-001"
    assert state.strategy_name == "RSI"
    assert state.price == 262.6
    assert state.ema20 == 260
    assert state.snapshot_time == snapshot.snapshot_time
