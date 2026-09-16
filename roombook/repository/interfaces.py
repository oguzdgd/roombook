"""Storage interfaces. service/ depends only on these — never on a concrete implementation."""

from __future__ import annotations

from typing import Protocol

from roombook.domain.models import Booking, Room


class RoomRepository(Protocol):
    def get(self, room_id: str) -> Room | None: ...


class BookingRepository(Protocol):
    def list_for_room(self, room_id: str) -> list[Booking]: ...

    def add(self, booking: Booking) -> None: ...
