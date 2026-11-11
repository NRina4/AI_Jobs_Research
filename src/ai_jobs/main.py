from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from ai_jobs.api.endpoints import analytics, reference, vacancies
from ai_jobs.core.config import get_settings
from ai_jobs.services.exceptions import ReferenceNotFoundError

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    description=(
        "REST API информационной системы анализа рынка труда в сфере ИИ: "
        "управление вакансиями, ETL-данные, аналитика и бизнес-операции."
    ),
)


def error_response(
    status_code: int,
    error: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "error": error,
        "message": message,
        "detail": message if details is None else details,
    }
    if details is not None:
        payload["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request error"
    details = exc.detail if not isinstance(exc.detail, str) else None
    return error_response(exc.status_code, "http_error", message, details=details)


@app.exception_handler(ReferenceNotFoundError)
async def reference_not_found_handler(
    request: Request, exc: ReferenceNotFoundError
) -> JSONResponse:
    return error_response(404, "not_found", str(exc))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        422,
        "validation_error",
        "Request validation failed",
        details=jsonable_encoder(exc.errors()),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return error_response(422, "unprocessable_entity", str(exc))


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    return error_response(
        409,
        "conflict",
        "Operation conflicts with existing data",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response(500, "internal_error", "Internal server error")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
def read_index():
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(
    vacancies.router,
    prefix="/api/v1",
)

app.include_router(
    analytics.router,
    prefix="/api/v1",
)

app.include_router(
    reference.router,
    prefix="/api/v1",
)
