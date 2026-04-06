from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def register_middlewares(app: FastAPI) -> None:
    @app.middleware('http')
    async def request_logging_middleware(request: Request, call_next):
        response = await call_next(request)
        logger.info('%s %s -> %s', request.method, request.url.path, response.status_code)
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception):
        logger.exception('Unhandled exception: %s', exc)
        return JSONResponse(status_code=500, content={'detail': 'Internal server error'})
