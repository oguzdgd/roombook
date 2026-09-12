"""In-memory implementations of the repository interfaces. V1 storage: no persistence."""

from __future__ import annotations

from roombook.domain.models import Booking, Room


class InMemoryRoomRepository:
    def __init__(self, rooms: list[Room] | None = None) -> None:
        self._rooms: dict[str, Room] = {room.id: room for room in (rooms or [])}

    def get(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def add(self, room: Room) -> None:
        self._rooms[room.id] = room


class InMemoryBookingRepository:
    def __init__(self) -> None:
        self._bookings_by_room: dict[str, list[Booking]] = {}

    def list_for_room(self, room_id: str) -> list[Booking]:
        return list(self._bookings_by_room.get(room_id, []))

    def add(self, booking: Booking) -> None:
        self._bookings_by_room.setdefault(booking.room_id, []).append(booking)
