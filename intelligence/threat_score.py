HIGH_RISK = [
    "wget", "curl", "nc", "bash", "sh", "python", "perl", "ruby", 
    "gcc", "make", "./", "chmod +x", "cat /etc/passwd", "cat /etc/shadow",
    "cat passwd", "cat shadow", "/bin/sh", "/bin/bash"
]
MEDIUM_RISK = [
    "sudo", "chmod", "chown", "whoami", "id", "uname", 
    "cat", "tail", "head", "history", "ps", "kill"
]

def calculate_score(command: str) -> int:
    cmd = command.lower()
    
    # Critical checks first
    if any(k in cmd for k in HIGH_RISK):
        return 90
        
    # Medium checks
    if any(k in cmd for k in MEDIUM_RISK):
        return 50
        
    # Low risk (navigation)
    return 10
