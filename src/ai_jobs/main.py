from fastapi import FastAPI

from ai_jobs.api.endpoints import analytics, vacancies
from ai_jobs.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(
    vacancies.router,
    prefix="/api/v1",
)

app.include_router(
    analytics.router,
    prefix="/api/v1",
)
