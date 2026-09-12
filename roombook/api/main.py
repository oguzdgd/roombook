from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from roombook.api.routers.bookings import router as bookings_router
from roombook.api.schemas import ErrorResponse


def create_app() -> FastAPI:
    app = FastAPI(title="RoomBook")
    app.include_router(bookings_router)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="invalid_input", message="invalid request body"
            ).model_dump(),
        )

    return app


app = create_app()
