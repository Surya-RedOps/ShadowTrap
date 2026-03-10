from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from database.session import get_db
from database.models import SSHSession

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard_home():
    html_path = Path("dashboard/index.html")
    return html_path.read_text()


@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SSHSession).order_by(SSHSession.id.desc()).limit(50).all()

    return [
        {
            "ip": s.ip_address,
            "username": s.username,
            "command": s.command,
            "risk": s.risk_score,
            "time": s.timestamp,
        }
        for s in sessions
    ]
