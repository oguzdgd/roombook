"""Business rules: booking creation, conflict detection (BR-1..BR-3), free-slot suggestions."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime, timedelta

from roombook.domain.clock import Clock
from roombook.domain.models import Booking, TimeSlot
from roombook.repository.interfaces import BookingRepository, RoomRepository
from roombook.service.errors import BookingConflictError, InvalidTimeSlotError, RoomNotFoundError

MAX_SUGGESTIONS = 3
SUGGESTION_HORIZON = timedelta(days=7)


def _slots_overlap(a: TimeSlot, b: TimeSlot) -> bool:
    return a.start < b.end and b.start < a.end


def _find_free_slots(
    existing: list[Booking],
    requested_start: datetime,
    duration: timedelta,
    horizon_end: datetime,
    max_suggestions: int = MAX_SUGGESTIONS,
) -> list[TimeSlot]:
    relevant = sorted(
        (b.slot for b in existing if b.slot.end > requested_start and b.slot.start < horizon_end),
        key=lambda slot: slot.start,
    )

    suggestions: list[TimeSlot] = []
    cursor = requested_start
    for slot in relevant:
        if len(suggestions) >= max_suggestions or cursor >= horizon_end:
            break
        if slot.start > cursor and (slot.start - cursor) >= duration:
            suggestions.append(TimeSlot(start=cursor, end=cursor + duration))
        cursor = max(cursor, slot.end)

    if len(suggestions) < max_suggestions and horizon_end - cursor >= duration:
        suggestions.append(TimeSlot(start=cursor, end=cursor + duration))

    return suggestions[:max_suggestions]


def create_booking(
    *,
    room_id: str,
    slot: TimeSlot,
    organizer: str,
    title: str,
    rooms: RoomRepository,
    bookings: BookingRepository,
    clock: Clock,
    id_factory: Callable[[], str] = lambda: str(uuid.uuid4()),
) -> Booking:
    room = rooms.get(room_id)
    if room is None:
        raise RoomNotFoundError(room_id)

    if slot.start.tzinfo is None or slot.end.tzinfo is None:
        raise InvalidTimeSlotError("start and end must be timezone-aware timestamps")

    if not slot.end > slot.start:
        raise InvalidTimeSlotError("end must be strictly after start")

    if slot.start < clock.now():
        raise InvalidTimeSlotError("start must not be in the past")

    existing = bookings.list_for_room(room_id)
    conflicts = sorted(
        (b for b in existing if _slots_overlap(b.slot, slot)),
        key=lambda b: b.slot.start,
    )
    if conflicts:
        duration = slot.end - slot.start
        horizon_end = slot.start + SUGGESTION_HORIZON
        suggestions = _find_free_slots(existing, slot.start, duration, horizon_end)
        raise BookingConflictError(conflicts=conflicts, suggestions=suggestions)

    booking = Booking(
        id=id_factory(),
        room_id=room_id,
        slot=slot,
        organizer=organizer,
        title=title,
    )
    bookings.add(booking)
    return booking
