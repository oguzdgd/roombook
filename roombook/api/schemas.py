"""Wire format only — request/response schemas. No business logic here."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateBookingRequest(BaseModel):
    room_id: str
    start: datetime
    end: datetime
    organizer: str = Field(min_length=1)
    title: str = Field(min_length=1)


class BookingResponse(BaseModel):
    id: str
    room_id: str
    start: datetime
    end: datetime
    organizer: str
    title: str


class ConflictDetail(BaseModel):
    start: datetime
    end: datetime
    title: str


class SuggestedSlot(BaseModel):
    start: datetime
    end: datetime


class ConflictResponse(BaseModel):
    error: str = "conflict"
    conflicts: list[ConflictDetail]
    suggestions: list[SuggestedSlot]


class ErrorResponse(BaseModel):
    error: str
    message: str
