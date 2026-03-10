from core.logger import logger
from database.db import SessionLocal
from database.models import ThreatEvent

class ThreatScoringEngine:
    def __init__(self):
        self.scores = {
            "recon": 1,
            "persistence": 2,
            "priv_esc": 3,
            "malware": 4,
            "critical": 10
        }
    
    def calculate_risk(self, ip, tactic):
        """Update threat score for an IP based on the MITRE tactic."""
        points = 0
        if tactic in ["Discovery", "Collection"]:
            points = self.scores["recon"]
        elif tactic in ["Persistence"]:
            points = self.scores["persistence"]
        elif tactic in ["Privilege Escalation"]:
            points = self.scores["priv_esc"]
        elif tactic in ["Command and Control"]:
            points = self.scores["malware"]
        elif tactic in ["Exfiltration", "Impact"]:
            points = self.scores["critical"]
        
        # Always update the database to ensure the IP is tracked as a threat actor
        self._update_db(ip, points)
        
        return points

    def _update_db(self, ip, points):
        db = SessionLocal()
        event = db.query(ThreatEvent).filter(ThreatEvent.ip_address == ip).first()
        
        if not event:
            event = ThreatEvent(ip_address=ip, total_score=points)
            db.add(event)
        else:
            event.total_score += points
        
        # Re-classify
        if event.total_score > 20:
            event.classification = "Active Threat Actor"
        elif event.total_score > 10:
            event.classification = "Medium Risk"
        else:
            event.classification = "Low Risk"
            
        db.commit()
        db.close()

threat_engine = ThreatScoringEngine()
