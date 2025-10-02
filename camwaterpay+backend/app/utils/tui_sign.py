import hmac, hashlib
from datetime import datetime
from app.core.config import settings

def sign_tui(txn_id: str, meter_id: int, user_id: int, amount: str, expires_at: datetime, card_uid_lock: str | None):
    msg = f"{txn_id}|{meter_id}|{user_id}|{amount}|{int(expires_at.timestamp())}|{card_uid_lock or ''}"
    return hmac.new(settings.TUI_SIGNING_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
