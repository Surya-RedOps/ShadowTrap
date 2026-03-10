FROM python:3.12-slim

# Install system dependencies if any (none strictly required for current setup)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure storage directories exist
RUN mkdir -p database/malware logs

# Expose ports
# 8000: Dashboard
# 2222: SSH Honeypot
EXPOSE 8000 2222

# Run the platform
CMD ["python", "main.py"]
