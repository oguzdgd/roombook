"""Domain shapes: Room, TimeSlot, Booking.

Plain dataclasses only — no FastAPI/Pydantic imports here (docs/architecture.md forbidden-deps
rule). Business-rule validation (BR-1..BR-3) lives in service/, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Booking:
    id: str
    room_id: str
    slot: TimeSlot
    organizer: str
    title: str
