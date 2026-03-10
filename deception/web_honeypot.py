from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import SessionLocal
from database.models import WebCredential
from intelligence.threat_score import calculate_score
from intelligence.telegram_alert import send_telegram_alert
from pathlib import Path

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def fake_login_page():
    return Path("deception/templates/login.html").read_text()


@router.post("/login")
def capture_credentials(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = request.client.host
    risk = calculate_score("web_login_attempt")

    db = SessionLocal()

    cred = WebCredential(
        ip_address=ip,
        username=username,
        password=password,
        risk_score=risk,
    )
    db.add(cred)
    db.commit()
    db.close()

    # Telegram alert
    message = (
        "🚨 *ShadowTrap Web Credential Capture*\n\n"
        f"*IP:* `{ip}`\n"
        f"*User:* `{username}`\n"
        f"*Pass:* `{password}`\n"
        f"*Risk:* `{risk}`"
    )
    send_telegram_alert(message)

    return RedirectResponse(url="/login", status_code=302)
