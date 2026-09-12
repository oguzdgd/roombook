from __future__ import annotations

from fastapi import FastAPI

from roombook.api.routers.bookings import router as bookings_router


def create_app() -> FastAPI:
    app = FastAPI(title="RoomBook")
    app.include_router(bookings_router)
    return app


app = create_app()
