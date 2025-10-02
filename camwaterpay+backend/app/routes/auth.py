from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.utils.security import hash_secret, verify_secret, create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/register")
async def register(payload: dict, db: AsyncSession = Depends(get_db)):
    mobile = payload.get("mobile","").strip()
    secret_word = payload.get("secret_word","").strip().lower()
    pin = payload.get("pin","")
    if not mobile or not secret_word or not pin:
        raise HTTPException(status_code=400, detail="Missing fields")
    q = await db.execute(select(User).where(User.mobile == mobile))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Mobile already registered")
    u = User(mobile=mobile, secret_word_hash=hash_secret(secret_word), pin_hash=hash_secret(pin))
    db.add(u); await db.commit()
    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
async def login(payload: dict, db: AsyncSession = Depends(get_db)):
    mobile = payload.get("mobile","").strip(); pin = payload.get("pin","")
    q = await db.execute(select(User).where(User.mobile == mobile))
    u = q.scalar_one_or_none()
    if not u or not verify_secret(pin, u.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}

RESET_TOKENS = {}

@router.post("/forgot/start")
async def forgot_start(payload: dict, db: AsyncSession = Depends(get_db)):
    mobile = payload.get("mobile","").strip()
    q = await db.execute(select(User).where(User.mobile == mobile))
    u = q.scalar_one_or_none()
    if not u:
        return {"message": "If the mobile exists, proceed with verification."}
    tok = create_access_token(f"reset:{u.id}")
    RESET_TOKENS[u.mobile] = tok
    return {"message": "Provide your secret word to verify.", "reset_hint": "secret_word"}

@router.post("/forgot/verify")
async def forgot_verify(payload: dict, db: AsyncSession = Depends(get_db)):
    mobile = payload.get("mobile","").strip(); secret = payload.get("secret_word","").strip().lower()
    q = await db.execute(select(User).where(User.mobile == mobile))
    u = q.scalar_one_or_none()
    if not u or not verify_secret(secret, u.secret_word_hash):
        raise HTTPException(status_code=400, detail="Verification failed")
    tok = RESET_TOKENS.get(u.mobile)
    return {"reset_token": tok}

@router.post("/forgot/reset")
async def reset_pin(payload: dict, db: AsyncSession = Depends(get_db)):
    mobile = payload.get("mobile","").strip(); reset_token = payload.get("reset_token",""); new_pin = payload.get("new_pin","")
    q = await db.execute(select(User).where(User.mobile == mobile))
    u = q.scalar_one_or_none()
    if not u or reset_token != RESET_TOKENS.get(u.mobile):
        raise HTTPException(status_code=400, detail="Invalid reset token")
    await db.execute(update(User).where(User.id == u.id).values(pin_hash=hash_secret(new_pin)))
    await db.commit(); RESET_TOKENS.pop(u.mobile, None)
    return {"message": "PIN updated"}
