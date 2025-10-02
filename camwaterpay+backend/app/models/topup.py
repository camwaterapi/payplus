from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class TopUp(Base):
    __tablename__ = "topups"
    id = Column(Integer, primary_key=True)
    txn_id = Column(String(64), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meter_id = Column(Integer, ForeignKey("meters.id"))
    amount = Column(Numeric(12,2), nullable=False)
    currency = Column(String(8), nullable=False)
    method = Column(String(16), nullable=False)  # stripe|flutterwave
    status = Column(String(32), default="INITIATED")
    gateway_ref = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User")
    meter = relationship("Meter")
