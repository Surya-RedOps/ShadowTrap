import time
from intelligence.mitre import get_mitre_info

class BehaviorAnalyzer:
    def __init__(self):
        self.session_data = {}  # {ip: {'last_cmd_time': float, 'commands': [], 'typing_speeds': []}}

    def analyze(self, ip, command_line):
        current_time = time.time()
        
        if ip not in self.session_data:
            self.session_data[ip] = {
                'start_time': current_time,
                'last_cmd_time': current_time,
                'commands': [],
                'inter_arrival_times': [],
                'tactics': set()
            }
        
        session = self.session_data[ip]
        
        # Calculate time since last command
        time_diff = current_time - session['last_cmd_time']
        session['inter_arrival_times'].append(time_diff)
        session['last_cmd_time'] = current_time
        session['commands'].append(command_line)
        
        # MITRE Mapping
        mitre_info = get_mitre_info(command_line)
        if mitre_info:
            session['tactics'].add(mitre_info['tactic'])
            
        return self._classify(session)

    def _classify(self, session):
        # Heuristics
        avg_speed = sum(session['inter_arrival_times']) / len(session['inter_arrival_times']) if session['inter_arrival_times'] else 0
        cmd_count = len(session['commands'])
        
        attacker_type = "Unknown"
        
        if avg_speed < 0.2 and cmd_count > 5:
            attacker_type = "Automated Bot"
        elif avg_speed < 2.0:
            attacker_type = "Script Kiddie (Copy/Paste)"
        else:
            attacker_type = "Human Actor"
            
        return {
            "attacker_type": attacker_type,
            "avg_inter_arrival": round(avg_speed, 2),
            "tactics": list(session['tactics'])
        }

behavior_engine = BehaviorAnalyzer()
