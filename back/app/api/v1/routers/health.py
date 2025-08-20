# app/api/v1/routers/health.py
# (проверка работы эндпоинтов)
from fastapi import APIRouter

from app.utils.http_helpers import op_endpoint
from app.db.schemas.result import OperationResult

router = APIRouter()

@router.get("/hello")
@op_endpoint
async def hello():
    res = OperationResult.ok(message="Проверка работы роутеров показала - ok.")
    return res
