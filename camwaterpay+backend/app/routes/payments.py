from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.topup import TopUp
from app.models.user import User
from app.routes.meters import current_user
from app.core.config import settings
from app.utils.ids import new_txn_id
import stripe, httpx, os

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/init")
async def init_topup(payload: dict, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    meter_id = int(payload.get("meter_id"))
    amount = float(payload.get("amount"))
    method = payload.get("method")
    txn_id = new_txn_id()
    t = TopUp(txn_id=txn_id, user_id=user.id, meter_id=meter_id, amount=amount, currency=settings.CURRENCY, method=method)
    db.add(t); await db.commit(); await db.refresh(t)

    if method == "stripe":
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price_data": {"currency": settings.CURRENCY.lower(), "product_data": {"name": f"Top-up {txn_id}"}, "unit_amount": int(float(amount)*100)}, "quantity": 1}],
            success_url=f"{os.getenv('FRONTEND_URL','http://localhost:5173')}/pay/return?txn_id={txn_id}",
            cancel_url=f"{os.getenv('FRONTEND_URL','http://localhost:5173')}/meters",
            metadata={"topup_id": str(t.id), "txn_id": txn_id}
        )
        return {"topup_id": t.id, "txn_id": txn_id, "checkout_url": session.url}

    elif method == "flutterwave":
        headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}", "Content-Type": "application/json"}
        payload_flw = {
            "tx_ref": txn_id, "amount": str(amount), "currency": settings.CURRENCY,
            "redirect_url": f"{os.getenv('FRONTEND_URL','http://localhost:5173')}/pay/return?txn_id={txn_id}",
            "customer": {"email": f"user{user.id}@example.com", "phonenumber": user.mobile, "name": f"User{user.id}"},
            "payment_options": "card, mobilemoney"
        }
        async with httpx.AsyncClient() as client:
            r = await client.post("https://api.flutterwave.com/v3/payments", headers=headers, json=payload_flw)
            r.raise_for_status(); data = r.json(); link = data.get("data", {}).get("link")
        return {"topup_id": t.id, "txn_id": txn_id, "checkout_url": link}

    else:
        raise HTTPException(status_code=400, detail="Unsupported method")

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    if event["type"] == "checkout.session.completed":
        meta = event["data"]["object"].get("metadata", {})
        topup_id = int(meta.get("topup_id"))
        q = await db.execute(select(TopUp).where(TopUp.id == topup_id))
        t = q.scalar_one_or_none()
        if t:
            t.status = "PAID"; t.gateway_ref = meta.get("txn_id"); await db.commit()
    return {"ok": True}

@router.post("/webhook/flutterwave")
async def flw_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    secret = settings.FLW_WEBHOOK_SECRET
    verif = request.headers.get("verif-hash")
    if not secret or verif != secret:
        raise HTTPException(status_code=401, detail="Invalid signature")
    body = await request.json()
    status = body.get("status"); tx_ref = body.get("txRef") or body.get("tx_ref")
    if status and status.lower() in ("successful", "completed") and tx_ref:
        q = await db.execute(select(TopUp).where(TopUp.txn_id == tx_ref))
        t = q.scalar_one_or_none()
        if t:
            t.status = "PAID"; t.gateway_ref = tx_ref; await db.commit()
    return {"ok": True}
