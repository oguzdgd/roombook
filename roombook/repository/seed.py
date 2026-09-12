"""Fixed example rooms used to seed the running app. Tests never depend on this — they inject
their own fixture room via dependency override (see tests/conftest.py)."""

from __future__ import annotations

from roombook.domain.models import Room

SEED_ROOMS: list[Room] = [
    Room(id="room-1", name="Alpha", capacity=6),
    Room(id="room-2", name="Bravo", capacity=12),
]
