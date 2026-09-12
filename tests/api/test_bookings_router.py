from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from roombook.api.dependencies import get_bookings_repo, get_clock, get_rooms_repo
from roombook.api.main import create_app
from roombook.domain.models import Room
from roombook.repository.in_memory import InMemoryBookingRepository, InMemoryRoomRepository
from tests.conftest import FIXED_NOW, FixedClock


@pytest.fixture
def client(test_room: Room) -> TestClient:
    app = create_app()
    rooms_repo = InMemoryRoomRepository([test_room])
    bookings_repo = InMemoryBookingRepository()
    app.dependency_overrides[get_rooms_repo] = lambda: rooms_repo
    app.dependency_overrides[get_bookings_repo] = lambda: bookings_repo
    app.dependency_overrides[get_clock] = lambda: FixedClock(FIXED_NOW)
    return TestClient(app)


def _iso(offset_hours: float) -> str:
    return (FIXED_NOW + timedelta(hours=offset_hours)).isoformat()


# AC-1 — happy path
def test_create_booking_returns_201(client: TestClient, test_room: Room) -> None:
    response = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": _iso(1),
            "end": _iso(2),
            "organizer": "Alice",
            "title": "Sync",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["room_id"] == test_room.id
    assert body["organizer"] == "Alice"
    assert body["title"] == "Sync"
    assert "id" in body


# AC-11 — unknown room, 404, distinguishable from conflict/invalid
def test_unknown_room_returns_404(client: TestClient) -> None:
    response = client.post(
        "/bookings",
        json={
            "room_id": "no-such-room",
            "start": _iso(1),
            "end": _iso(2),
            "organizer": "Alice",
            "title": "Sync",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "room_not_found"


# AC-12 — invalid window (end not after start), 422, distinguishable from conflict/not-found
def test_invalid_window_returns_422(client: TestClient, test_room: Room) -> None:
    response = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": _iso(2),
            "end": _iso(2),
            "organizer": "Alice",
            "title": "Sync",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_time_slot"


# AC-14 — missing/empty organizer or title, 422 (Pydantic-level validation)
def test_missing_organizer_or_title_returns_422(client: TestClient, test_room: Room) -> None:
    response = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": _iso(1),
            "end": _iso(2),
            "organizer": "",
            "title": "Sync",
        },
    )
    assert response.status_code == 422


# AC-15 — naive timestamp (no timezone), 422, distinguishable from a conflict rejection
def test_naive_timestamp_returns_422(client: TestClient, test_room: Room) -> None:
    naive_start = (FIXED_NOW + timedelta(hours=1)).replace(tzinfo=None).isoformat()
    naive_end = (FIXED_NOW + timedelta(hours=2)).replace(tzinfo=None).isoformat()
    response = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": naive_start,
            "end": naive_end,
            "organizer": "Alice",
            "title": "Sync",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_time_slot"


# Conflict end-to-end: 409 with conflicts + suggestions
def test_conflicting_booking_returns_409_with_details(client: TestClient, test_room: Room) -> None:
    first = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": _iso(1),
            "end": _iso(2),
            "organizer": "Alice",
            "title": "Standup",
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/bookings",
        json={
            "room_id": test_room.id,
            "start": _iso(1),
            "end": _iso(2),
            "organizer": "Bob",
            "title": "Retro",
        },
    )
    assert second.status_code == 409
    body = second.json()
    assert body["error"] == "conflict"
    assert body["conflicts"][0]["title"] == "Standup"
    assert len(body["suggestions"]) >= 1
