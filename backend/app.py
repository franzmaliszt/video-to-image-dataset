import os

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from api.routers import test_router

load_dotenv()

app = FastAPI()
app.include_router(test_router)

@app.on_event("startup")
async def startup():
    pass
