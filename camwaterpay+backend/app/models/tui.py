from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.models.base import Base

class TUI(Base):
    __tablename__ = "tuis"
    id = Column(Integer, primary_key=True)
    topup_id = Column(Integer, ForeignKey("topups.id"), index=True)
    txn_id = Column(String(64), unique=True, index=True)
    meter_id = Column(Integer)
    user_id = Column(Integer)
    amount = Column(String(32))
    expires_at = Column(DateTime)
    card_uid_lock = Column(String(32), nullable=True)
    signature = Column(String(128))
    status = Column(String(24), default="READY")  # READY|USED|EXPIRED
    proof_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
