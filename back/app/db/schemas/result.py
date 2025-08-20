# back/app/utils/result.py
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from enum import Enum
from app.core.logging import logger
import traceback

class Status(str, Enum):
    OK = "ok"
    FAIL = "fail"    # бизнес-ошибка / валидация
    ERROR = "error"  # исключение / инфраструктурная ошибка

@dataclass
class OperationResult:
    status: Status
    message: str = ""
    data: Optional[Any] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @staticmethod
    def ok(data: Any = None, message: str = "ok", meta: Dict[str, Any] = None):
        meta = meta or {}
        res = OperationResult(Status.OK, message, data, meta, None)
        logger.info(f"[OK] {message} meta={meta}")
        return res

    @staticmethod
    def fail(message: str = "fail", data: Any = None, meta: Dict[str, Any] = None):
        meta = meta or {}
        res = OperationResult(Status.FAIL, message, data, meta, None)
        logger.warning(f"[FAIL] {message} meta={meta}")
        return res

    @staticmethod
    def error(message: str = "error", exc: Exception = None, meta: Dict[str, Any] = None):
        meta = meta or {}
        err_text = None
        if exc is not None:
            err_text = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            logger.error(f"[ERROR] {message} exc={err_text}", exc_info=exc)
        else:
            logger.error(f"[ERROR] {message}")
        return OperationResult(Status.ERROR, message, None, meta, err_text)

    def to_http(self, success_code: int = 200):
        """Преобразовать в тело ответа FastAPI. Не отправляет ответ сам."""
        if self.status == Status.OK:
            return {"status": self.status.value, "message": self.message, "data": self.data}
        if self.status == Status.FAIL:
            return {"status": self.status.value, "message": self.message, "data": self.data}
        # ERROR
        return {"status": self.status.value, "message": self.message, "error": self.error}
