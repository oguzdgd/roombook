"""FastAPI dependency providers. Overridden in tests via app.dependency_overrides.

Depends only on roombook.service.wiring — never on roombook.repository directly
(docs/architecture.md forbidden-deps rule).
"""

from __future__ import annotations

from roombook.domain.clock import Clock
from roombook.service.wiring import (
    BookingRepository,
    RoomRepository,
    get_default_bookings_repo,
    get_default_clock,
    get_default_rooms_repo,
)

__all__ = [
    "BookingRepository",
    "RoomRepository",
    "get_bookings_repo",
    "get_clock",
    "get_rooms_repo",
]


def get_rooms_repo() -> RoomRepository:
    return get_default_rooms_repo()


def get_bookings_repo() -> BookingRepository:
    return get_default_bookings_repo()


def get_clock() -> Clock:
    return get_default_clock()
