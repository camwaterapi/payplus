from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.config import settings
from app.models.tui import TUI
from app.models.topup import TopUp
from app.utils.card_profile import CardProfile
from app.services.desfire_ev2 import EV2Session, first_apdu_for_session, next_apdu

router = APIRouter()
SESSIONS = {}
PROFILE = CardProfile.load()
CRYPTO_PROVIDER = settings.CARD_CRYPTO_PROVIDER  # mock|hsm|disabled

@router.post("/sessions/start")
async def start_session(tui_id: int, uid: str | None = None, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TUI).where(TUI.id == tui_id))
    tui = q.scalar_one_or_none()
    if not tui or tui.status != "READY":
        raise HTTPException(status_code=400, detail="Invalid TUI")
    if tui.expires_at and tui.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="TUI expired")
    if not PROFILE or CRYPTO_PROVIDER == 'disabled':
        if settings.ENABLE_REMOTE_APPLY_FALLBACK:
            raise HTTPException(status_code=409, detail="CARD_PROFILE_UNAVAILABLE_USE_REMOTE_APPLY")
        else:
            raise HTTPException(status_code=503, detail="Card writing temporarily unavailable")
    if tui.card_uid_lock and uid and tui.card_uid_lock.upper() != uid.upper():
        raise HTTPException(status_code=400, detail="Card not allowed for this TUI")

    sid = f"sess-{tui.txn_id}"
    SESSIONS[sid] = {"tui_id": tui_id, "uid": uid, "sess": EV2Session(uid=uid or "", txn_id=tui.txn_id)}
    return {"session_id": sid, "apdu": first_apdu_for_session()}

@router.post("/sessions/step")
async def session_step(session_id: str, card_resp_hex: str, db: AsyncSession = Depends(get_db)):
    s = SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    q = await db.execute(select(TUI).where(TUI.id == s["tui_id"]))
    tui = q.scalar_one_or_none()
    if not tui:
        raise HTTPException(status_code=404, detail="TUI not found")
    decimals = PROFILE.decimals if PROFILE else 0
    amount_units = int(round(float(tui.amount) * (10 ** decimals)))
    ledger = f"{tui.txn_id}|{tui.user_id}|{tui.meter_id}".encode()
    return next_apdu(s["sess"], card_resp_hex, amount_units, ledger)

@router.post("/sessions/finish")
async def session_finish(session_id: str, proof_hash: str, db: AsyncSession = Depends(get_db)):
    s = SESSIONS.pop(session_id, None)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    q = await db.execute(select(TUI).where(TUI.id == s["tui_id"]))
    tui = q.scalar_one_or_none()
    if not tui:
        raise HTTPException(status_code=404, detail="TUI not found")
    tui.status = "USED"; tui.proof_hash = proof_hash
    await db.commit()
    q2 = await db.execute(select(TopUp).where(TopUp.txn_id == tui.txn_id))
    t = q2.scalar_one_or_none()
    if t:
        t.status = "LOADED_TO_CARD"; await db.commit()
    return {"message": "Card written. Present card to meter."}
