import os
import time

from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv


load_dotenv()
logger = get_task_logger(__name__)

worker = Celery(__name__)
worker.config_from_object("config")