# app/api/v1/api.py
# (включает остальные роутеры)
from fastapi import APIRouter
from .routers import health, auth

router_v1 = APIRouter()
router_v1.include_router(health.router, prefix="", tags=["health"])
router_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
# TODO: добавить routers: router.include_router(contracts.router, prefix="/contracts")
