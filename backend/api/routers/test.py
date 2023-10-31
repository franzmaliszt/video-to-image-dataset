from fastapi import APIRouter

from ..workers.worker import worker


test_router = APIRouter(prefix="/test")

@test_router.get("/hello/{text}")
async def test(text: str):
    task = worker.send_task("hello_task", args=[text])
    return {"message": f"Hello {text}", "task_id": task.id}

@test_router.get("/sum/{x}/{y}")
async def test(x: int, y: int):
    task = worker.send_task("add_task", args=[x, y])
    return {"task_id": task.id}

@test_router.post("/hello")
async def test_post():
    task = worker.send_task("sample_loop_task")
    return {"task_id": task.id}
