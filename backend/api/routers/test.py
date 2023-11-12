import logging
from itertools import islice
from typing import Iterable

from fastapi import APIRouter

from api.workers.worker import worker
from api.models import SubmitModel


logger = logging.getLogger(__name__)

test_router = APIRouter(prefix="/test")


def batchify(iterable: Iterable, batch_size: int = 10):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch

@test_router.get("/hello/{text}")
async def test(text: str):
    task = worker.send_task("hello_task", args=[text])
    return {"task_id": task.id}

@test_router.post("/hello")
async def test_post():
    task = worker.send_task("sample_loop_task")
    return {"task_id": task.id}


@test_router.post("/submit")
async def submit(payload: SubmitModel, output_size: int = 20):
    task = worker.send_task(
        "submit_task", args=[payload.video, payload.images, output_size]
    ) #TODO: Process videos and images in different tasks
    return {"task_id": task.id}
