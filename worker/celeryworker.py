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
    logger.info(f"Hello {text}")
    print(f"pHello {text}")
    time.sleep(3)
    logger.info(f"Done saying hello to {text}")
    print(f"pDone saying hello to {text}")
    return f"Hello {text}"

@app.task(name="add_task")
def add(x: int, y: int) -> int:
    logger.info(f"Adding {x} and {y}")
    time.sleep(3)
    logger.info(f"Done adding {x} and {y}")
    return x + y

@app.task(name="sample_loop_task")
def sample_task():
    for i in range(5):
        logger.info(f"Task {i} started!")
        time.sleep(5)
    print(f"Task {i} completed!")
