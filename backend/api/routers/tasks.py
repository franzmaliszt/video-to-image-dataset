from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..workers.worker import worker


tasks_router = APIRouter(prefix="/tasks")


@tasks_router.get("/{id}")
async def get_status(id: str):
    task_result = worker.AsyncResult(id)
    result = {
        "id": task_result.id,
        "status": task_result.status,
        "result": task_result.result,
    }
    return JSONResponse(result)