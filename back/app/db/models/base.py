# app/db/base.py
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr, as_declarative

@as_declarative()
class Base:
    id: any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class AuditMixin:
    """Миксин для soft-delete и штампов времени."""
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now(), nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # если not None => помечено как удалённое

    def mark_deleted(self, when: datetime = None):
        self.deleted_at = when or datetime.now()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
