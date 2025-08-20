from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.models.base import Base  # тут все модели должны быть импортированы в Base

async def init_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        # удаляет и создает заново, если хочешь чистый старт
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# if __name__ == "__main__":
#     asyncio.run(init_models(engine))
