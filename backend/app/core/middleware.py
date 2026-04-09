from time import perf_counter
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from app.db.session import SessionLocal
from app.repositories.audit_log_repository import AuditLogRepository

logger = logging.getLogger(__name__)


def register_middlewares(app: FastAPI) -> None:
    def _write_api_audit(request: Request, status_code: int, duration_ms: float) -> None:
        # Do not record health probes to keep audit logs focused on platform actions.
        if request.url.path == '/health':
            return
        if not request.url.path.startswith('/api/'):
            return

        admin_email = request.headers.get('X-Admin-Email', '').strip().lower()
        result = 'success' if status_code < 400 else 'error'
        payload = {
            'method': request.method,
            'path': request.url.path,
            'query': request.url.query,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'admin_email': admin_email or None,
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent', ''),
        }

        db = SessionLocal()
        try:
            AuditLogRepository(db).create(
                module_name='api_request',
                action_name=f'{request.method} {request.url.path}',
                payload=payload,
                result=result,
            )
        except Exception:
            logger.exception('Audit log write failed for %s %s', request.method, request.url.path)
        finally:
            db.close()

    @app.middleware('http')
    async def request_logging_middleware(request: Request, call_next):
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            logger.exception('%s %s -> 500 (%.2fms)', request.method, request.url.path, duration_ms)
            _write_api_audit(request, 500, duration_ms)
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        logger.info('%s %s -> %s (%.2fms)', request.method, request.url.path, response.status_code, duration_ms)
        _write_api_audit(request, response.status_code, duration_ms)
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception):
        logger.exception('Unhandled exception: %s', exc)
        return JSONResponse(status_code=500, content={'detail': 'Internal server error'})
