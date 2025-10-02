from fastapi import FastAPI
from app.core.config import settings
from app.routes import auth, payments, topups, nfc, meters, luna
from app.services.bootstrap import create_all

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def on_start():
    await create_all()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(meters.router, prefix="/meters", tags=["meters"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(topups.router, prefix="/topups", tags=["topups"])
app.include_router(nfc.router, prefix="/nfc", tags=["nfc"])
app.include_router(luna.router, prefix="/luna", tags=["luna"])

@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "env": settings.APP_ENV}
