import os
import time

from celery import Celery, current_task
from celery.utils.log import get_task_logger
from dotenv import load_dotenv


load_dotenv()
logger = get_task_logger(__name__)

app = Celery(__name__)
app.config_from_object("config")

@app.task(name="hello_task")
def hello(text: str) -> str:
    time.sleep(3)
    return f"Hello {text}"

@app.task(name="add_task")
def add(x: int, y: int) -> int:
    time.sleep(3)
    return x + y

@app.task(name="sample_loop_task")
def sample_task():
    for i in range(5):
        time.sleep(5)
    print(f"Task {i} completed!")
