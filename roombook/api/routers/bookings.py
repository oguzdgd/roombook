"""POST /bookings — status-code mapping only. Business logic lives in service/."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from roombook.api.dependencies import get_bookings_repo, get_clock, get_rooms_repo
from roombook.api.schemas import (
    BookingResponse,
    ConflictDetail,
    ConflictResponse,
    CreateBookingRequest,
    ErrorResponse,
    SuggestedSlot,
)
from roombook.domain.clock import Clock
from roombook.domain.models import TimeSlot
from roombook.repository.interfaces import BookingRepository, RoomRepository
from roombook.service.booking_service import create_booking
from roombook.service.errors import BookingConflictError, InvalidTimeSlotError, RoomNotFoundError

router = APIRouter()


@router.post("/bookings", status_code=201, response_model=BookingResponse)
def create_booking_endpoint(
    request: CreateBookingRequest,
    rooms: Annotated[RoomRepository, Depends(get_rooms_repo)],
    bookings: Annotated[BookingRepository, Depends(get_bookings_repo)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> BookingResponse | JSONResponse:
    try:
        booking = create_booking(
            room_id=request.room_id,
            slot=TimeSlot(start=request.start, end=request.end),
            organizer=request.organizer,
            title=request.title,
            rooms=rooms,
            bookings=bookings,
            clock=clock,
        )
    except RoomNotFoundError:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(error="room_not_found", message="room not found").model_dump(),
        )
    except InvalidTimeSlotError:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="invalid_time_slot", message="invalid booking time window"
            ).model_dump(),
        )
    except BookingConflictError as exc:
        body = ConflictResponse(
            conflicts=[
                ConflictDetail(start=b.slot.start, end=b.slot.end, title=b.title)
                for b in exc.conflicts
            ],
            suggestions=[SuggestedSlot(start=s.start, end=s.end) for s in exc.suggestions],
        )
        return JSONResponse(status_code=409, content=body.model_dump(mode="json"))

    return BookingResponse(
        id=booking.id,
        room_id=booking.room_id,
        start=booking.slot.start,
        end=booking.slot.end,
        organizer=booking.organizer,
        title=booking.title,
    )
