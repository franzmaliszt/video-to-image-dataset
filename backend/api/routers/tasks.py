from fastapi import APIRouter

from ..workers.worker import worker


tasks_router = APIRouter(prefix="/tasks")

@tasks_router.get("/{id}")
async def get_task(id: str):
    task = worker.AsyncResult(id)
    return {"task_id": task.id, "status": task.status, "result": task.result}
