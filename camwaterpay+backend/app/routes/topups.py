from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models.topup import TopUp
from app.models.tui import TUI
from app.routes.meters import current_user
from app.utils.tui_sign import sign_tui

router = APIRouter()

@router.get("/{topup_id}")
async def get_topup(topup_id: int, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TopUp).where(TopUp.id == topup_id, TopUp.user_id == user.id))
    t = q.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": t.id, "txn_id": t.txn_id, "status": t.status, "amount": str(t.amount), "currency": t.currency}

@router.get("/by-txn/{txn_id}")
async def get_topup_by_txn(txn_id: str, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TopUp).where(TopUp.txn_id == txn_id, TopUp.user_id == user.id))
    t = q.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Top-up not found")
    return {"id": t.id, "txn_id": t.txn_id, "status": t.status, "amount": str(t.amount), "currency": t.currency, "meter_id": t.meter_id}

@router.post("/{topup_id}/tui")
async def create_tui(topup_id: int, card_uid_lock: str | None = None, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TopUp).where(TopUp.id == topup_id, TopUp.user_id == user.id))
    t = q.scalar_one_or_none()
    if not t or t.status != "PAID":
        raise HTTPException(status_code=400, detail="Top-up not paid or not found")
    exp = datetime.utcnow() + timedelta(minutes=settings.TUI_EXP_MINUTES)
    sig = sign_tui(t.txn_id, t.meter_id, t.user_id, str(t.amount), exp, card_uid_lock)
    tui = TUI(topup_id=t.id, txn_id=t.txn_id, meter_id=t.meter_id, user_id=t.user_id, amount=str(t.amount), expires_at=exp, card_uid_lock=card_uid_lock, signature=sig)
    db.add(tui); await db.commit(); await db.refresh(tui)
    return {"tui_id": tui.id, "txn_id": tui.txn_id, "expires_at": tui.expires_at, "signature": tui.signature, "card_uid_lock": tui.card_uid_lock}
