import os

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from api.routers import test_router, tasks_router

load_dotenv()

app = FastAPI()
app.include_router(test_router)
app.include_router(tasks_router)
