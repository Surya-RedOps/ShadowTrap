class PatternAnalyzer:
    def __init__(self):
        self.patterns = {
            "Malware Deployment": ["wget", "chmod", "+x", "./"],
            "Crypto Miner Installation": ["wget", "tar", "xmrig", "start.sh"],
            "Reverse Shell Attempt": ["nc", "-e", "/bin/sh"],
            "Privilege Escalation": ["sudo", "su", "passwd", "shadow"],
            "Persistence Attempt": ["crontab", "-e", "@reboot"],
        }

    def detect_patterns(self, command_sequence):
        """Analyze a sequence of commands for known attack patterns."""
        matches = []
        # Joins all commands into a single string for substring matching (simple approach)
        full_seq = " ".join(command_sequence).lower()
        
        for name, keywords in self.patterns.items():
            if all(k.lower() in full_seq for k in keywords):
                matches.append(name)
        
        return matches

pattern_engine = PatternAnalyzer()
