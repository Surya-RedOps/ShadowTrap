from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from database.session import get_db
import os
from intelligence.analytics import (
    get_total_attacks,
    get_risk_distribution,
    get_top_ip,
    get_recent_activity,
    get_top_commands,
    get_attack_frequency_by_hour,
    get_geo_distribution
)

router = APIRouter()

def verify_auth(request: Request):
    # Simple hardcoded session check for dashboard security
    if request.cookies.get("shadow_session") == "AUTHORIZED_USER":
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/login")
async def login(data: dict, response: Response):
    password = data.get("password")
    env_pass = os.getenv("DASHBOARD_PASSWORD", "admin123")
    
    if password == env_pass:
        response.set_cookie(key="shadow_session", value="AUTHORIZED_USER", httponly=True)
        return {"status": "success"}
    
    raise HTTPException(status_code=401, detail="Invalid password")


@router.get("/stats", dependencies=[Depends(verify_auth)])
def soc_stats(db: Session = Depends(get_db)):
    return {
        "total_attacks": get_total_attacks(db),
        "top_ip": get_top_ip(db),
        "risk_distribution": get_risk_distribution(db),
    }

@router.get("/stats/malware", dependencies=[Depends(verify_auth)])
def soc_malware_stats(db: Session = Depends(get_db)):
    from intelligence.analytics import get_malware_stats
    return get_malware_stats(db)

@router.get("/threat-actors", dependencies=[Depends(verify_auth)])
def soc_threat_actors(db: Session = Depends(get_db)):
    from intelligence.analytics import get_top_threat_actors
    actors = get_top_threat_actors(db)
    return [
        {
            "ip": a.ip_address,
            "score": a.total_score,
            "classification": a.classification,
            "last_seen": str(a.last_seen)
        }
        for a in actors
    ]


@router.get("/activity", dependencies=[Depends(verify_auth)])
def soc_activity(db: Session = Depends(get_db)):
    activity = get_recent_activity(db, limit=100)

    return [
        {
            "ip": a.ip_address,
            "user": a.username,
            "command": a.command,
            "risk_score": a.risk_score,
            "attacker_type": a.attacker_type,
            "mitre_tactic": a.mitre_tactic,
            "time": str(a.timestamp),
        }
        for a in activity
    ]




@router.get("/analytics/top-commands", dependencies=[Depends(verify_auth)])
def soc_top_commands(db: Session = Depends(get_db)):
    return get_top_commands(db)

@router.get("/analytics/hourly", dependencies=[Depends(verify_auth)])
def analytics_hourly(db: Session = Depends(get_db)):
    return get_attack_frequency_by_hour(db)

@router.get("/analytics/geo", dependencies=[Depends(verify_auth)])
def soc_geo_analytics(db: Session = Depends(get_db)):
    return get_geo_distribution(db)
@router.post("/clear-stats", dependencies=[Depends(verify_auth)])
def clear_stats(db: Session = Depends(get_db)):
    from database.models import SSHSession, WebCredential
    db.query(SSHSession).delete()
    db.query(WebCredential).delete()
    db.commit()
    return {"status": "cleared"}

@router.post("/simulate", dependencies=[Depends(verify_auth)])
async def simulate_event(data: dict):
    from dashboard.live_ws import manager
    await manager.broadcast(data)
    
    # Trigger Telegram alert for simulation if risk is high
    if data.get("risk_score", 0) > 80:
        from intelligence.telegram_alert import send_telegram_alert
        msg = f"🛡️ **ShadowTrap SIMULATION ALERT**\n\n"
        msg += f"IP: `{data.get('ip')}`\n"
        msg += f"Country: {data.get('location', {}).get('country')}\n"
        msg += f"Cmd: `{data.get('command')}`\n"
        msg += f"Risk: `{data.get('risk_score')}`"
        send_telegram_alert(msg)
        
    return {"status": "event_simulated"}
