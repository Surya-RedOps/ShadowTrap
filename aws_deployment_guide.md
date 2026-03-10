# ShadowTrap: AWS EC2 Deployment Guide

Follow these steps to deploy ShadowTrap securely on an AWS EC2 instance.

## 1. Prepare your EC2 Instance
- **OS**: Ubuntu 22.04 LTS (Recommended)
- **Security Group**: Open the following ports:
  - **TCP 80**: Dashboard (via Nginx)
  - **TCP 22**: SSH Honeypot (via Nginx)
  - **TCP 2222**: Your **Real** SSH access (Required if you change host SSH)

## 2. Important: Avoid SSH Conflict
By default, EC2 uses port 22 for your real SSH. ShadowTrap's honeypot also wants port 22.
1. Change your real SSH port:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change 'Port 22' to 'Port 2222'
   sudo systemctl restart ssh
   ```
2. **Warning**: Ensure port 2222 is open in your AWS Security Group before doing this, or you will be locked out!

## 3. Install Docker & Docker Compose
Run these on your EC2 instance:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

## 4. Deploy ShadowTrap
1. Clone your project or upload the files to your EC2 instance.
2. Ensure your `.env` file is configured with your Telegram credentials and a strong `DASHBOARD_PASSWORD`.
3. Launch the platform:
```bash
sudo docker-compose up -d --build
```

## 5. Verification
- **Dashboard**: Visit `http://your-ec2-ip/soc-ui` and log in with your password.
- **Honeypot**: From your local machine, attempt to connect:
  ```bash
  ssh -p 22 root@your-ec2-ip
  ```
- **Alerts**: You should receive a Telegram notification for the connection.

## 6. Post-Deployment Security
- **HTTPS**: For production, consider using Certbot (Let's Encrypt) to enable HTTPS on Nginx.
- **Database**: The SQLite database and malware samples are stored in the `./database` volume on the host for persistence.
