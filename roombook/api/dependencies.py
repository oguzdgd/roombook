"""FastAPI dependency providers. Overridden in tests via app.dependency_overrides."""

from __future__ import annotations

from roombook.domain.clock import Clock, SystemClock
from roombook.repository.in_memory import InMemoryBookingRepository, InMemoryRoomRepository
from roombook.repository.interfaces import BookingRepository, RoomRepository
from roombook.repository.seed import SEED_ROOMS

_rooms_repo = InMemoryRoomRepository(SEED_ROOMS)
_bookings_repo = InMemoryBookingRepository()
_clock = SystemClock()


def get_rooms_repo() -> RoomRepository:
    return _rooms_repo


def get_bookings_repo() -> BookingRepository:
    return _bookings_repo


def get_clock() -> Clock:
    return _clock
