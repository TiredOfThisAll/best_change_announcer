from data.models.base import Base


async def create_schema(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
