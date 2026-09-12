from __future__ import annotations

from datetime import UTC, datetime

import pytest

from roombook.domain.clock import Clock
from roombook.domain.models import Room
from roombook.repository.in_memory import InMemoryBookingRepository, InMemoryRoomRepository

FIXED_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def clock() -> Clock:
    return FixedClock(FIXED_NOW)


@pytest.fixture
def test_room() -> Room:
    return Room(id="test-room", name="Test Room", capacity=4)


@pytest.fixture
def rooms_repo(test_room: Room) -> InMemoryRoomRepository:
    return InMemoryRoomRepository([test_room])


@pytest.fixture
def bookings_repo() -> InMemoryBookingRepository:
    return InMemoryBookingRepository()
