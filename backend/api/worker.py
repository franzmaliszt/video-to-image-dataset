import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()

worker = Celery("worker")
worker.conf.broker_url = os.environ["CELERY_BROKER_URL"]
worker.conf.result_backend = os.environ["CELERY_RESULT_BACKEND"]
