from celery.result import AsyncResult
from fastapi import APIRouter
from app.workers.celery_app import celery_app

router = APIRouter()


@router.get('/status')
def worker_status() -> dict:
    return {'status': 'ok'}


@router.get('/task/{task_id}')
def task_status(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None,
    }
