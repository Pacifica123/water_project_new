# app/crud/generic.py
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type
from sqlalchemy import select, update as sa_update, delete as sa_delete, insert as sa_insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from app.db.schemas import OperationResult
from app.core.logging import logger
from datetime import datetime
import asyncio

ModelType = Type[Any]
PKType = Any

# Параметры защиты: глобальный семафор для тяжелых batch-операций.
# Можно заменить на конфигируемый через settings.
BULK_MAX_CONCURRENCY = 4
_bulk_semaphore = asyncio.BoundedSemaphore(BULK_MAX_CONCURRENCY)

DEFAULT_BATCH = 500

# helper
async def _acquire_sem():
    await _bulk_semaphore.acquire()

def _release_sem():
    try:
        _bulk_semaphore.release()
    except ValueError:
        # уже отпущен — игнорируем
        pass


# ---------- CREATE ----------
async def create_entity(session: AsyncSession, model: ModelType, payload: Dict[str, Any]) -> OperationResult:
    """
    Создать одну сущность.
    :param session: AsyncSession
    :param model: ORM-класс (SQLAlchemy mapped class)
    :param payload: словарь полей (обычно предыдущая Pydantic-валидация)
    :return: OperationResult с data = ORM instance
    """
    try:
        obj = model(**payload)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return OperationResult.ok(data=obj, message="created")
    except Exception as exc:
        return OperationResult.error("create_entity failed", exc)

async def bulk_create(
    session: AsyncSession,
    model: Type[Any],
    rows: Sequence[Dict[str, Any]],
    batch_size: int = DEFAULT_BATCH,
    return_ids: bool = False,
) -> OperationResult:
    """
    Пакетная вставка с защитой семафором.
    :param session: AsyncSession
    :param model: ORM-класс
    :param rows: список dict
    :param batch_size: размер батча для каждой вставки
    :param return_ids: попытаться вернуть PK (Postgres RETURNING)
    :return: OperationResult
    """
    if not rows:
        return OperationResult.ok(data=[], message="no_rows")

    await _acquire_sem()
    logger.info("bulk_create: acquired semaphore")
    try:
        table = model.__table__
        ids = [] if return_ids else None
        for i in range(0, len(rows), batch_size):
            chunk = rows[i : i + batch_size]
            stmt = sa_insert(table).values(chunk)
            if return_ids:
                stmt = stmt.returning(*table.primary_key)
                res = await session.execute(stmt)
                # SQLAlchemy result.fetchall() may be sync; use .all() via scalars if needed
                fetched = res.fetchall()
                for r in fetched:
                    ids.append(tuple(r) if len(r) > 1 else r[0])
            else:
                await session.execute(stmt)
        return OperationResult.ok(data=ids, message="bulk_created")
    except Exception as exc:
        logger.exception("bulk_create failed")
        return OperationResult.error("bulk_create failed", exc)
    finally:
        _release_sem()
        logger.info("bulk_create: released semaphore")


# ---------- READ ----------
async def read_entity(session: AsyncSession, model: ModelType, pk: PKType,
                      pk_field: Optional[Any] = None, options: Optional[List[Any]] = None) -> OperationResult:
    """
    Прочитать одну запись по первичному ключу.
    :param pk_field: можно передать столбец PK, иначе берётся первый PK модели
    :param options: список options (selectinload/joinedload) для предотвращения N+1
    :return: OperationResult.data = ORM instance or None
    """
    try:
        pk_field = pk_field or list(model.__table__.primary_key)[0]
        stmt = select(model).where(pk_field == pk)
        if options:
            for opt in options:
                stmt = stmt.options(opt)
        res = await session.execute(stmt)
        obj = res.scalars().first()
        if not obj:
            return OperationResult.fail("not_found")
        return OperationResult.ok(data=obj, message="fetched")
    except Exception as exc:
        return OperationResult.error("read_entity failed", exc)

async def query_entities(session: AsyncSession, model: ModelType,
                         filters: Optional[Sequence[Any]] = None,
                         order_by: Optional[Sequence[Any]] = None,
                         offset: Optional[int] = None, limit: Optional[int] = None,
                         options: Optional[List[Any]] = None, include_deleted: bool = False) -> OperationResult:
    """
    Гибкий запрос. Возвращает OperationResult.data = dict{items: [...], total: int}
    :param include_deleted: если False — исключаем помеченные deleted_at != NULL (soft delete)
    """
    try:
        base: Select = select(model)
        if options:
            for opt in options:
                base = base.options(opt)
        if filters:
            for f in filters:
                base = base.where(f)
        if not include_deleted and hasattr(model, "deleted_at"):
            base = base.where(getattr(model, "deleted_at") == None)
        count_stmt = select(func.count()).select_from(base.subquery())
        if order_by:
            base = base.order_by(*order_by)
        if offset is not None:
            base = base.offset(offset)
        if limit is not None:
            base = base.limit(limit)

        rows_res = await session.execute(base)
        rows = rows_res.scalars().all()

        cnt_res = await session.execute(count_stmt)
        total = int(cnt_res.scalar_one())

        return OperationResult.ok(data={"items": rows, "total": total}, message="queried")
    except Exception as exc:
        return OperationResult.error("query_entities failed", exc)

# ---------- UPDATE ----------
async def update_entity(session: AsyncSession, model: ModelType, pk: PKType, values: Dict[str, Any],
                        pk_field: Optional[Any] = None, return_obj: bool = True) -> OperationResult:
    """
    Обновить одну запись по PK.
    :param values: словарь полей для обновления
    :param return_obj: если True — вернёт свежий ORM объект в data
    """
    try:
        pk_field = pk_field or list(model.__table__.primary_key)[0]
        table = model.__table__
        # автоматически обновляем updated_at если есть
        if hasattr(model, "updated_at"):
            values["updated_at"] = datetime.utcnow()
        stmt = sa_update(table).where(pk_field == pk).values(**values).returning(*table.primary_key)
        await session.execute(stmt)
        if return_obj:
            return await read_entity(session, model, pk, pk_field=pk_field)
        return OperationResult.ok(message="updated")
    except Exception as exc:
        return OperationResult.error("update_entity failed", exc)

async def bulk_update(
    session: AsyncSession,
    model: ModelType,
    updates: Sequence[Tuple[PKType, Dict[str, Any]]],
    pk_field: Optional[Any] = None,
    batch_size: int = DEFAULT_BATCH,
) -> OperationResult:
    """
    Пакетное обновление: updates = [(pk, {field: val}), ...]
    """
    if not updates:
        return OperationResult.ok(message="no_updates")

    await _acquire_sem()
    logger.info("bulk_update: acquired semaphore")

    try:
        table = model.__table__
        pk_field = pk_field or list(table.primary_key)[0]

        for i in range(0, len(updates), batch_size):
            chunk = updates[i : i + batch_size]
            async with session.begin():
                for pk, vals in chunk:
                    if hasattr(model, "updated_at"):
                        vals["updated_at"] = datetime.utcnow()
                    stmt = sa_update(table).where(pk_field == pk).values(**vals)
                    await session.execute(stmt)

        return OperationResult.ok(message="bulk_updated")

    except Exception as exc:
        logger.exception("bulk_update failed")
        return OperationResult.error("bulk_update failed", exc)

    finally:
        _release_sem()
        logger.info("bulk_update: released semaphore")

# ---------- DELETE (soft by default) ----------
async def delete_entity(session: AsyncSession, model: ModelType, pk: PKType,
                        pk_field: Optional[Any] = None, hard: bool = False) -> OperationResult:
    """
    Удаление одной записи.
    :param hard: если True — физическое удаление. Иначе — soft delete (deleted_at = now).
    """
    try:
        pk_field = pk_field or list(model.__table__.primary_key)[0]
        table = model.__table__
        if hard:
            stmt = sa_delete(table).where(pk_field == pk)
            await session.execute(stmt)
            return OperationResult.ok(message="deleted_hard")
        else:
            vals = {}
            if hasattr(model, "deleted_at"):
                vals["deleted_at"] = datetime.utcnow()
            if hasattr(model, "updated_at"):
                vals["updated_at"] = datetime.utcnow()
            stmt = sa_update(table).where(pk_field == pk).values(**vals)
            await session.execute(stmt)
            return OperationResult.ok(message="deleted_soft")
    except Exception as exc:
        return OperationResult.error("delete_entity failed", exc)

async def bulk_delete(
    session: AsyncSession,
    model: ModelType,
    pks: Sequence[PKType],
    pk_field: Optional[Any] = None,
    hard: bool = False,
    batch_size: int = DEFAULT_BATCH,
) -> OperationResult:
    if not pks:
        return OperationResult.ok(message="no_pks")

    await _acquire_sem()
    logger.info("bulk_delete: acquired semaphore")

    try:
        table = model.__table__
        pk_field = pk_field or list(table.primary_key)[0]

        for i in range(0, len(pks), batch_size):
            chunk = pks[i : i + batch_size]
            if hard:
                stmt = sa_delete(table).where(pk_field.in_(chunk))
                await session.execute(stmt)
            else:
                vals = {}
                utcnow = datetime.utcnow()
                if hasattr(model, "deleted_at"):
                    vals["deleted_at"] = utcnow
                if hasattr(model, "updated_at"):
                    vals["updated_at"] = utcnow
                stmt = sa_update(table).where(pk_field.in_(chunk)).values(**vals)
                await session.execute(stmt)

        return OperationResult.ok(message="bulk_deleted")

    except Exception as exc:
        logger.exception("bulk_delete failed")
        return OperationResult.error("bulk_delete failed", exc)

    finally:
        _release_sem()
        logger.info("bulk_delete: released semaphore")
