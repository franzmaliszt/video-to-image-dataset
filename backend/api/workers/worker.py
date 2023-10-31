from celery import Celery
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

worker = Celery(__name__)
worker.config_from_object("api.workers.config")