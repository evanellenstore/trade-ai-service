from datetime import timedelta

import pytest

from app.config.settings import Settings
from app.models.trading_state import TradingState
from app.services.context_service import ContextService


class FakeDecisionService:
    def __init__(self):
        self.calls = []

    async def evaluate(self, signal, snapshot):
        self.calls.append((signal, snapshot))


@pytest.mark.asyncio
async def test_context_correlates_signal_and_snapshot(signal, snapshot):
    service = FakeDecisionService()
    context = ContextService(Settings(), service)

    await context.handle_message("signal.generated", signal.model_dump(by_alias=True))
    assert service.calls == []
    await context.handle_message("market.snapshot", snapshot.model_dump(by_alias=True))

    assert len(service.calls) == 1
    assert service.calls[0][0].signal_id == "SIG-001"
    assert context._signals == {}


def test_trading_state_accepts_snapshot_candles(signal, snapshot):
    state = TradingState.from_events(signal, snapshot)

    assert state.symbol == signal.symbol
    assert state.candles == []


@pytest.mark.asyncio
async def test_context_pairs_events_when_timestamps_are_close(signal, snapshot):
    service = FakeDecisionService()
    context = ContextService(Settings(), service)
    near_signal = signal.model_copy(update={"timestamp": snapshot.snapshot_time + timedelta(seconds=3)})

    await context.handle_message("signal.generated", near_signal.model_dump(by_alias=True))
    await context.handle_message("market.snapshot", snapshot.model_dump(by_alias=True))

    assert len(service.calls) == 1
    assert service.calls[0][0].signal_id == "SIG-001"


@pytest.mark.asyncio
async def test_context_does_not_pair_stale_timestamped_events(signal, snapshot):
    service = FakeDecisionService()
    context = ContextService(Settings(), service)
    stale_signal = signal.model_copy(update={"timestamp": snapshot.snapshot_time.replace(year=2025)})

    await context.handle_message("signal.generated", stale_signal.model_dump(by_alias=True))
    await context.handle_message("market.snapshot", snapshot.model_dump(by_alias=True))

    assert service.calls == []
