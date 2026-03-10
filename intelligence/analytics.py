from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import SSHSession, MalwareSample, ThreatEvent
from intelligence.geoip_engine import geoip_engine


def get_total_attacks(db: Session):
    return db.query(SSHSession).count()


def get_risk_distribution(db: Session):
    # Distribution of ALL attacks based on risk score
    low = db.query(SSHSession).filter(SSHSession.risk_score <= 30).count()
    med = db.query(SSHSession).filter(SSHSession.risk_score.between(31, 70)).count()
    high = db.query(SSHSession).filter(SSHSession.risk_score > 70).count()
    
    return {
        "Low Risk": low,
        "Medium Risk": med,
        "Active Threat Actor": high
    }


def get_top_ip(db: Session):
    result = (
        db.query(SSHSession.ip_address, func.count().label("c"))
        .group_by(SSHSession.ip_address)
        .order_by(func.count().desc())
        .first()
    )
    if not result:
        return None
    return {"ip": result[0], "count": result[1]}

def get_malware_stats(db: Session):
    return {
        "total_captured": db.query(MalwareSample).count(),
        "unique_samples": db.query(func.count(func.distinct(MalwareSample.sha256))).scalar() or 0
    }

def get_top_threat_actors(db: Session, limit=5):
    return db.query(ThreatEvent).order_by(ThreatEvent.total_score.desc()).limit(limit).all()

def get_top_commands(db: Session, limit: int = 5):
    # Group by command, ignoring empty sequences
    results = db.query(SSHSession.command, func.count(SSHSession.command).label('count')) \
                 .filter(SSHSession.command != '') \
                 .group_by(SSHSession.command) \
                 .order_by(func.count(SSHSession.command).desc()) \
                 .limit(limit) \
                 .all()
    # Explicitly convert to dicts for clean JSON serialization
    return [{"command": r[0], "count": r[1]} for r in results]

def get_attack_frequency_by_hour(db: Session):
    return db.query(func.strftime('%H', SSHSession.timestamp).label('hour'), func.count(SSHSession.id)) \
             .group_by('hour') \
             .all()

def get_geo_distribution(db: Session):
    ips = db.query(SSHSession.ip_address).distinct().all()
    distribution = {}
    for ip in ips:
        if not ip or not ip[0]:
            continue
        ip_str = ip[0]
        
        # Don't skip internal for stats, just label them, so the chart isn't empty
        location = geoip_engine.get_location(ip_str)
        country = location.get("country", "Unknown")
        distribution[country] = distribution.get(country, 0) + 1
    
    result = [{"country": k, "count": v} for k, v in distribution.items()]
    return result if result else [{"country": "Awaiting Traffic", "count": 0}]

def get_recent_activity(db: Session, limit: int = 10):
    return (
        db.query(SSHSession)
        .order_by(SSHSession.timestamp.desc())
        .limit(limit)
        .all()
    )
