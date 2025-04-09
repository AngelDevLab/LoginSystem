from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from config import settings
from fastapi.middleware.cors import CORSMiddleware

from lib import app_token
import dependencies
from routers import user_routes, admin
import logging
from lib import database as my_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def app_startup():
    logging.info("---------- Application startup ----------")
    my_db.table_user_info_init()

def app_shutdown():
    logging.info("---------- Application shutdown ----------")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_startup()
    yield
    app_shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    user_routes.router,
    prefix="/user"
)

app.include_router(
    admin.router,
    prefix="/admin"
)


#uvicorn main:app --reload

from datetime import datetime

@app.get("/time")
async def test():
    return datetime.now()
