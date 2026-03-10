import os

# Node Identity
NODE_ID = os.getenv("NODE_ID", "node-01")

# Central Server (for future use)
CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://localhost:8000/api/collect")

# Honeypot Settings
SSH_PORT = int(os.getenv("SSH_PORT", 2222))
WEB_PORT = int(os.getenv("WEB_PORT", 8000))
