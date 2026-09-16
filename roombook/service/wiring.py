"""Composition-root wiring: the only place a concrete repository implementation is chosen.

api/ must never import roombook.repository directly (docs/architecture.md forbidden-deps rule);
it depends only on this module's provider functions and re-exported interface types.
"""

from __future__ import annotations

from roombook.domain.clock import Clock, SystemClock
from roombook.repository.in_memory import InMemoryBookingRepository, InMemoryRoomRepository
from roombook.repository.interfaces import BookingRepository, RoomRepository
from roombook.repository.seed import SEED_ROOMS

__all__ = [
    "BookingRepository",
    "RoomRepository",
    "get_default_bookings_repo",
    "get_default_clock",
    "get_default_rooms_repo",
]

_rooms_repo: RoomRepository = InMemoryRoomRepository(SEED_ROOMS)
_bookings_repo: BookingRepository = InMemoryBookingRepository()
_clock: Clock = SystemClock()


def get_default_rooms_repo() -> RoomRepository:
    return _rooms_repo


def get_default_bookings_repo() -> BookingRepository:
    return _bookings_repo


def get_default_clock() -> Clock:
    return _clock
