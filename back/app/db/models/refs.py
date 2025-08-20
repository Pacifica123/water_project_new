from sqlalchemy import Column, Integer, String
from .base import Base, AuditMixin

class WaterPoolRef(Base, AuditMixin):
    __tablename__ = "water_pool_ref"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_name = Column(String(50), nullable=False)
