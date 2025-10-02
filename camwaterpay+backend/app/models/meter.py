from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Meter(Base):
    __tablename__ = "meters"
    id = Column(Integer, primary_key=True)
    meter_number = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    alias = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User")
