from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WaterPoolBase(BaseModel):
    pool_name: str


class WaterPoolCreate(WaterPoolBase):
    pass


class WaterPoolUpdate(BaseModel):
    pool_name: str | None = None


class WaterPoolRead(WaterPoolBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        orm_mode = True

