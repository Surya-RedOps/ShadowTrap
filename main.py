from fastapi import FastAPI
import asyncio

from core.logger import logger

# Honeypots
from deception.ssh_honeypot import start_ssh_honeypot
from deception.web_honeypot import router as web_router

# Database
from database.db import engine, Base

# Dashboards & APIs
from dashboard.routes import router as dashboard_router
from dashboard.soc_api import router as soc_router
from dashboard.soc_view import router as soc_view_router
from dashboard.live_route import router as live_router


app = FastAPI(title="ShadowTrap", version="0.3")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting ShadowTrap honeypots + SOC engine...")
    Base.metadata.create_all(bind=engine)

    # Start SSH honeypot in background
    asyncio.create_task(start_ssh_honeypot())


# ---------- ROUTE ORDER MATTERS ----------

# SOC UI FIRST
app.include_router(soc_view_router, prefix="/soc-ui")

# SOC analytics API
app.include_router(soc_router, prefix="/soc", tags=["SOC"])

# Existing APIs
app.include_router(dashboard_router, prefix="/api")
app.include_router(web_router, prefix="/web")

# WebSocket
app.include_router(live_router)


@app.get("/")
def root():
    return {"message": "ShadowTrap is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
