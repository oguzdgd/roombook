"""Typed domain errors. api/ maps each to an HTTP status (docs/conventions.md)."""

from __future__ import annotations

from roombook.domain.models import Booking, TimeSlot


class RoomNotFoundError(Exception):
    def __init__(self, room_id: str) -> None:
        super().__init__(f"room not found: {room_id}")
        self.room_id = room_id


class InvalidTimeSlotError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class BookingConflictError(Exception):
    def __init__(self, conflicts: list[Booking], suggestions: list[TimeSlot]) -> None:
        super().__init__("booking conflicts with existing bookings")
        self.conflicts = conflicts
        self.suggestions = suggestions
