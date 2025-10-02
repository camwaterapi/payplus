from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.models.meter import Meter
from app.models.user import User
from app.core.config import settings
import jwt

router = APIRouter()

async def current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split()[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        uid = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    q = await db.execute(select(User).where(User.id == uid))
    u = q.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return u

@router.post("/link")
async def link_meter(meter_number: str, alias: str | None = None, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Meter).where(Meter.meter_number == meter_number))
    m = q.scalar_one_or_none()
    if not m:
        m = Meter(meter_number=meter_number, user_id=user.id, alias=alias)
        db.add(m)
    else:
        await db.execute(update(Meter).where(Meter.id == m.id).values(user_id=user.id, alias=alias or m.alias))
    await db.commit()
    return {"message": "Meter linked", "meter_id": m.id}

@router.get("")
async def list_meters(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Meter).where(Meter.user_id == user.id))
    items = q.scalars().all()
    return [{"id": i.id, "meter_number": i.meter_number, "alias": i.alias} for i in items]
