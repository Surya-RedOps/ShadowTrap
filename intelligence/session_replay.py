import json
import time
from database.db import SessionLocal
from database.models import AttackSession

class SessionReplayEngine:
    def __init__(self):
        self.sessions = {} # {session_id: [events]}

    def log_event(self, session_id, ip, event_type, data):
        """Log an event for session replay."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "ip": ip,
                "events": [],
                "start_time": time.time()
            }
        
        self.sessions[session_id]["events"].append({
            "timestamp": time.time(),
            "type": event_type,
            "data": data
        })

    def finalize_session(self, session_id):
        """Store the session in the database."""
        if session_id in self.sessions:
            session_data = self.sessions.pop(session_id)
            db = SessionLocal()
            
            db_session = AttackSession(
                session_id=session_id,
                ip_address=session_data["ip"],
                log_data=json.dumps(session_data["events"]),
                end_time=None # Set based on last event if needed
            )
            
            # Using merge in case it exists
            db.merge(db_session)
            db.commit()
            db.close()

replay_engine = SessionReplayEngine()
