from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database.db import Base


class SSHSession(Base):
    __tablename__ = "ssh_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) # Logical session ID
    ip_address = Column(String)
    username = Column(String)
    password = Column(String)
    command = Column(Text)
    risk_score = Column(Integer)
    attacker_type = Column(String, default="Unknown")
    mitre_tactic = Column(String, default="None")
    timestamp = Column(DateTime, default=datetime.utcnow)


class WebCredential(Base):
    __tablename__ = "web_credentials"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String)
    username = Column(String)
    password = Column(String)
    risk_score = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MalwareSample(Base):
    __tablename__ = "malware_samples"

    id = Column(Integer, primary_key=True, index=True)
    attacker_ip = Column(String)
    filename = Column(String)
    sha256 = Column(String)
    size = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AttackSession(Base):
    """Stores full session logs for replay."""
    __tablename__ = "attack_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    ip_address = Column(String)
    log_data = Column(Text) # JSON string of events
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)


class ThreatEvent(Base):
    """Aggregated threat events for a specific IP."""
    __tablename__ = "threat_events"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    total_score = Column(Integer, default=0)
    classification = Column(String, default="Low Risk")
    last_seen = Column(DateTime, default=datetime.utcnow)
