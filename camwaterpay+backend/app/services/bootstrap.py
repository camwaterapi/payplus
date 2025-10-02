from app.core.database import engine
from app.models.base import Base
from app.models import user, meter, topup, tui  # noqa

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
