import os

MITRE_MAPPING = {
    # Reconnaissance
    "ls": {"tactic": "Discovery", "id": "T1083", "name": "File and Directory Discovery"},
    "dir": {"tactic": "Discovery", "id": "T1083", "name": "File and Directory Discovery"},
    "pwd": {"tactic": "Discovery", "id": "T1083", "name": "File and Directory Discovery"},
    "whoami": {"tactic": "Discovery", "id": "T1033", "name": "System Owner/User Discovery"},
    "id": {"tactic": "Discovery", "id": "T1033", "name": "System Owner/User Discovery"},
    "w": {"tactic": "Discovery", "id": "T1033", "name": "System Owner/User Discovery"},
    "uname": {"tactic": "Discovery", "id": "T1082", "name": "System Information Discovery"},
    "cat": {"tactic": "Collection", "id": "T1005", "name": "Data from Local System"},
    "grep": {"tactic": "Collection", "id": "T1005", "name": "Data from Local System"},
    "ps": {"tactic": "Discovery", "id": "T1057", "name": "Process Discovery"},
    "netstat": {"tactic": "Discovery", "id": "T1049", "name": "System Network Connections Discovery"},
    "ss": {"tactic": "Discovery", "id": "T1049", "name": "System Network Connections Discovery"},
    "find": {"tactic": "Discovery", "id": "T1083", "name": "File and Directory Discovery"},
    "history": {"tactic": "Discovery", "id": "T1552", "name": "Unsecured Credentials"},

    # Execution
    "./": {"tactic": "Execution", "id": "T1059.004", "name": "Command and Scripting Interpreter: Unix Shell"},
    "bash": {"tactic": "Execution", "id": "T1059.004", "name": "Command and Scripting Interpreter: Unix Shell"},
    "sh": {"tactic": "Execution", "id": "T1059.004", "name": "Command and Scripting Interpreter: Unix Shell"},
    "python": {"tactic": "Execution", "id": "T1059.006", "name": "Command and Scripting Interpreter: Python"},
    "perl": {"tactic": "Execution", "id": "T1059", "name": "Command and Scripting Interpreter"},
    
    # Persistence / Privilege Escalation
    "sudo": {"tactic": "Privilege Escalation", "id": "T1548.003", "name": "Abuse Elevation Control Mechanism: Sudo and Sudo Caching"},
    "su": {"tactic": "Privilege Escalation", "id": "T1078", "name": "Valid Accounts"},
    "chmod": {"tactic": "Defense Evasion", "id": "T1222.002", "name": "File and Directory Permissions Modification: Linux and Mac File and Directory Permissions Modification"},
    "chown": {"tactic": "Defense Evasion", "id": "T1222.002", "name": "File and Directory Permissions Modification: Linux and Mac File and Directory Permissions Modification"},
    "touch": {"tactic": "Defense Evasion", "id": "T1070.006", "name": "Indicator Removal on Host: Timestomp"},
    "rm": {"tactic": "Defense Evasion", "id": "T1070.004", "name": "Indicator Removal on Host: File Deletion"},

    # Command and Control / Ingress Tool Transfer
    "wget": {"tactic": "Command and Control", "id": "T1105", "name": "Ingress Tool Transfer"},
    "curl": {"tactic": "Command and Control", "id": "T1105", "name": "Ingress Tool Transfer"},
    "scp": {"tactic": "Command and Control", "id": "T1105", "name": "Ingress Tool Transfer"},
    "sftp": {"tactic": "Command and Control", "id": "T1105", "name": "Ingress Tool Transfer"},
    "ssh": {"tactic": "Lateral Movement", "id": "T1021.004", "name": "Remote Services: SSH"},
}

def get_mitre_info(command_line):
    if not command_line:
        return None
    
    parts = command_line.split()
    cmd = parts[0]
    
    # Handle ./script.sh
    if cmd.startswith("./") or cmd.endswith(".sh"):
        return MITRE_MAPPING["./"]
        
    base_cmd = os.path.basename(cmd)
    
    return MITRE_MAPPING.get(base_cmd, None)

