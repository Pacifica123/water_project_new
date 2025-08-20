# back/app/utils/http_helpers.py
import functools
import inspect
from typing import Callable, Awaitable
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.db.schemas.result import OperationResult, Status

def _map_status_to_code(res: OperationResult) -> int:
    try:
        return int(res.meta.get("status_code"))
    except Exception:
        pass
    if res.status == Status.OK: return 200
    if res.status == Status.FAIL: return 400
    return 500

def result_to_response(res: OperationResult):
    status_code = _map_status_to_code(res)
    body = res.to_http()
    if res.status == Status.OK:
        return JSONResponse(status_code=status_code, content=body)
    # для FAIL и ERROR пробрасываем HTTPException (FastAPI отобразит detail)
    raise HTTPException(status_code=status_code, detail=body)

def op_endpoint(func: Callable[..., Awaitable[OperationResult]]):
    """
    Декоратор: сохраняет сигнатуру функции, чтобы FastAPI корректно
    обрабатывал зависимости и валидацию.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        res = await func(*args, **kwargs)
        return result_to_response(res)

    # критично: скопировать сигнатуру, чтобы FastAPI видел те же параметры
    wrapper.__signature__ = inspect.signature(func)
    return wrapper