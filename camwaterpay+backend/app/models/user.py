from sqlalchemy import Column, Integer, String, DateTime, func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    mobile = Column(String(20), unique=True, nullable=False, index=True)
    secret_word_hash = Column(String(255), nullable=False)
    pin_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
