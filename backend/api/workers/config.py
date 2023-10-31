import os

from dotenv import load_dotenv


load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
result_backend = os.getenv("CELERY_RESULT_BACKEND")
broker_connection_retry_on_startup = True