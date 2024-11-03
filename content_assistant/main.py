import content_assistant
import uvicorn
import logging.config
from content_assistant.core.config.logging import logging_config
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from content_assistant.core.config.settings import get_settings
from content_assistant.core.exceptions import (
    AppExceptionCase,
    app_exception_handler,
    request_validation_exception_handler,
    http_exception_handler,
)
from content_assistant.routers import collections_router, health_router

logging.config.dictConfig(logging_config)


def create_app() -> FastAPI:
    app = FastAPI(title="Content Authoring Assistant API", version=content_assistant.__version__)

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, e):
        return await http_exception_handler(request, e)

    @app.exception_handler(AppExceptionCase)
    async def custom_app_exception_handler(request, e):
        return await app_exception_handler(request, e)

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(request, e):
        return await request_validation_exception_handler(request, e)

    api_router = APIRouter()
    api_router.include_router(collections_router, prefix="/collections", tags=["content_generation"])
    api_router.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(api_router)

    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host=get_settings().uvicorn_host, port=get_settings().uvicorn_port)
