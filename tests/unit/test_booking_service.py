from __future__ import annotations

from datetime import timedelta

import pytest

from roombook.domain.clock import Clock
from roombook.domain.models import Room, TimeSlot
from roombook.repository.in_memory import InMemoryBookingRepository, InMemoryRoomRepository
from roombook.service.booking_service import create_booking
from roombook.service.errors import BookingConflictError, InvalidTimeSlotError, RoomNotFoundError
from tests.conftest import FIXED_NOW

Rooms = InMemoryRoomRepository
Bookings = InMemoryBookingRepository


def _slot(start_offset_hours: float, duration_hours: float = 1) -> TimeSlot:
    start = FIXED_NOW + timedelta(hours=start_offset_hours)
    end = start + timedelta(hours=duration_hours)
    return TimeSlot(start=start, end=end)


def _book(
    rooms_repo: Rooms,
    bookings_repo: Bookings,
    clock: Clock,
    test_room: Room,
    slot: TimeSlot,
    organizer: str = "Alice",
    title: str = "Sync",
) -> None:
    create_booking(
        room_id=test_room.id,
        slot=slot,
        organizer=organizer,
        title=title,
        rooms=rooms_repo,
        bookings=bookings_repo,
        clock=clock,
    )


# AC-1 / AC-9 — happy path, no existing bookings
def test_create_booking_succeeds(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    slot = _slot(1)
    booking = create_booking(
        room_id=test_room.id,
        slot=slot,
        organizer="Alice",
        title="Sync",
        rooms=rooms_repo,
        bookings=bookings_repo,
        clock=clock,
    )
    assert booking.room_id == test_room.id
    assert booking.slot == slot
    assert bookings_repo.list_for_room(test_room.id) == [booking]


def test_succeeds_when_room_has_no_existing_bookings(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    assert bookings_repo.list_for_room(test_room.id) == []
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(2))
    assert len(bookings_repo.list_for_room(test_room.id)) == 1


# AC-2 — exact match is a conflict
def test_exact_match_window_is_conflict(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 1))
    with pytest.raises(BookingConflictError) as exc_info:
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 1))
    assert len(exc_info.value.conflicts) == 1


# AC-3 — new start falls inside existing
def test_new_start_inside_existing_is_conflict(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 2))  # [1,3)
    with pytest.raises(BookingConflictError):
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(2, 2))  # [2,4)


# AC-4 — new end falls inside existing
def test_new_end_inside_existing_is_conflict(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(2, 2))  # [2,4)
    with pytest.raises(BookingConflictError):
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 2))  # [1,3)


# AC-5 — new window fully contains existing
def test_new_window_fully_contains_existing_is_conflict(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(2, 1))  # [2,3)
    with pytest.raises(BookingConflictError):
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 4))  # [1,5)


# AC-6 — touching slots are NOT conflicts, both directions
def test_touching_slots_before_and_after_are_not_conflicts(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(2, 1))  # [2,3)
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(3, 1))  # touches end: [3,4)
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 1))  # touches start: [1,2)
    assert len(bookings_repo.list_for_room(test_room.id)) == 3


# AC-7 — every overlap listed, ordered ascending by start
def test_conflict_lists_all_overlaps_ordered_by_start(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(5, 1), title="Second")  # [5,6)
    _book(rooms_repo, bookings_repo, clock, test_room, _slot(1, 1), title="First")  # [1,2)
    with pytest.raises(BookingConflictError) as exc_info:
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(0, 10))  # [0,10) overlaps both
    titles = [b.title for b in exc_info.value.conflicts]
    assert titles == ["First", "Second"]


# AC-8 — up to 3 suggestions, same duration, >= requested start, within 7 days
def test_conflict_suggests_up_to_three_matching_windows(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    duration = timedelta(hours=1)
    # Book hours 0,2,4,6,8 (1h each), leaving 1h gaps at hours 1,3,5,7 — five candidate
    # gaps, more than the 3-suggestion cap.
    for i in (0, 2, 4, 6, 8):
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(i, 1))
    # request conflicts with the first booking -> conflict, forcing suggestion search
    with pytest.raises(BookingConflictError) as exc_info:
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(0, 1))

    suggestions = exc_info.value.suggestions
    assert len(suggestions) == 3
    expected_starts = [FIXED_NOW + timedelta(hours=h) for h in (1, 3, 5)]
    assert [s.start for s in suggestions] == expected_starts
    for slot in suggestions:
        assert slot.end - slot.start == duration
        assert slot.start >= FIXED_NOW
        assert slot.start <= FIXED_NOW + timedelta(days=7)


# AC-10 — suggestions empty when nothing fits in the horizon
def test_suggestions_empty_when_no_free_window_fits_in_horizon(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    # Book the entire 7-day horizon solid with 1-hour bookings from FIXED_NOW.
    hours_in_horizon = 7 * 24
    for i in range(hours_in_horizon):
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(i, 1))
    with pytest.raises(BookingConflictError) as exc_info:
        _book(rooms_repo, bookings_repo, clock, test_room, _slot(0, 1))
    assert exc_info.value.suggestions == []


# AC-11 — unknown room
def test_unknown_room_raises_room_not_found(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock
) -> None:
    with pytest.raises(RoomNotFoundError):
        create_booking(
            room_id="does-not-exist",
            slot=_slot(1),
            organizer="Alice",
            title="Sync",
            rooms=rooms_repo,
            bookings=bookings_repo,
            clock=clock,
        )


# AC-12 — end not strictly after start
def test_end_not_after_start_raises_invalid_time_slot(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    start = FIXED_NOW + timedelta(hours=1)
    slot = TimeSlot(start=start, end=start)  # end == start, not strictly after
    with pytest.raises(InvalidTimeSlotError):
        _book(rooms_repo, bookings_repo, clock, test_room, slot)


# AC-13 — start strictly before now vs. start == now
def test_start_before_now_raises_invalid_time_slot(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    start = FIXED_NOW - timedelta(seconds=1)
    slot = TimeSlot(start=start, end=start + timedelta(hours=1))
    with pytest.raises(InvalidTimeSlotError):
        _book(rooms_repo, bookings_repo, clock, test_room, slot)


def test_start_equal_to_now_is_allowed(
    rooms_repo: Rooms, bookings_repo: Bookings, clock: Clock, test_room: Room
) -> None:
    slot = TimeSlot(start=FIXED_NOW, end=FIXED_NOW + timedelta(hours=1))
    _book(rooms_repo, bookings_repo, clock, test_room, slot)
    assert len(bookings_repo.list_for_room(test_room.id)) == 1
