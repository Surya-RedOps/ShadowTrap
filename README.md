# ShadowTrap - Advanced Deception Platform

ShadowTrap is a next-generation cybersecurity platform designed to **detect, deceive, and analyze** attackers in real-time. It features a high-interaction SSH honeypot and a live SOC dashboard for monitoring threats.

## 🚀 Features

- **High-Interaction SSH Honeypot**: Simulates a realistic Linux environment with a stateful **Virtual Filesystem** (create, delete, modify files).
- **Attacker Behavior Analysis**: Automatically classifies sessions as **Automated Bot**, **Script Kiddie**, or **Human Actor** based on timing and command patterns.
- **MITRE ATT&CK Mapping**: Maps executed commands to MITRE tactics (e.g., `wget` -> Ingress Tool Transfer) for standardized threat reporting.
- **Live Threat Perception**: Real-time WebSocket-based dashboard visualizing attacks, risk scores, and attacker classification.
- **Intelligence Gathering**: Captures keystrokes, commands, and attacker IP addresses for forensic analysis.
- **Post-Exploitation Traps**:
    - **False Privilege**: `sudo` commands always succeed, logging the attempt.
    - **Persistence Monitoring**: Tracks `crontab` usage.
    - **Honeytokens**: Fake AWS keys (`~/.aws/credentials`) and config files to trace attackers.

## 🏗️ Architecture

ShadowTrap is built on a **modular, event-driven architecture**:

### 1. The Core: SSH Honeypot (`deception/ssh_honeypot.py`)
- **Technology**: `asyncssh` + `asyncio`.
- **Function**: Handles thousands of concurrent SSH connections.
- **Virtual Filesystem (VFS)**: An in-memory object (`deception/filesystem.py`) that acts like a Linux file tree. It allows attackers to `cd`, `ls`, `mkdir`, `rm`, etc., without touching the host OS.

### 2. The Brain: Intelligence Engine (`intelligence/`)
- **Behavior Analysis**: Calculates Inter-Arrival Time (IAT) of keystrokes.
    - **Bots**: <10ms IAT.
    - **Humans**: >200ms IAT + typos.
- **MITRE Engine**: Matches commands against a threat database to identify tactics.

### 3. The Eyes: SOC Dashboard (`dashboard/`)
- **Backend**: FastAPI with WebSockets for real-time streaming.
- **Frontend**: `soc.html` (Vanilla JS + Chart.js) renders live attack maps and risk graphs.
- **Analytics**: Provides insights on Top Commands, Hourly Activity, and Risk Distribution.

### 4. Distributed Design
- Each instance has a configurable `NODE_ID`.
- Designed to be deployed as a network of sensors (honeypot mesh) reporting to a central collector.

## 📦 Installation & Usage

### 1. Docker Deployment (Recommended)
```bash
docker-compose up --build -d
```
- **Dashboard**: `http://localhost:8000/soc-ui/`
- **SSH Port**: `2222`

### 2. Manual Setup
```bash
# Create virtual env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Verification
Run the included test client to simulate an attack:
```bash
python tests/test_honeypot_client.py
```

## 📂 Project Structure
- `deception/`: Core honeypot logic & VFS.
- `intelligence/`: Analysis engines (Behavior, MITRE).
- `dashboard/`: Frontend and API.
- `database/`: storage for logs.
- `config/`: Configuration settings.
