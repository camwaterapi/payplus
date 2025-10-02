import jwt, time
from passlib.hash import bcrypt
from app.core.config import settings

def hash_secret(value: str) -> str: return bcrypt.hash(value)
def verify_secret(raw: str, hashed: str) -> bool: return bcrypt.verify(raw, hashed)
def create_access_token(sub: str) -> str:
    now = int(time.time()); exp = now + settings.ACCESS_TOKEN_EXPIRES_MIN * 60
    payload = {"sub": sub, "iat": now, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
