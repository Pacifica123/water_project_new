from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import router_v1
from app.db.init_db import init_models
from app.db.session import engine
from app.db.schemas.result import OperationResult
from app.utils.http_helpers import result_to_response
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models(engine=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    res = OperationResult.error("internal_error", exc=exc)
    return result_to_response(res)

origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "http://backend:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "*",
    ],
)

app.include_router(router_v1, prefix="/api/v1",)

# @app.get("/api/hello")
# def read_root():
#     return {"message": "Hello from FastAPI"}
