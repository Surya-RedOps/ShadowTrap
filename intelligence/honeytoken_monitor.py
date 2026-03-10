from core.logger import logger
from dashboard.live_ws import manager
from intelligence.telegram_alert import send_telegram_alert

class HoneytokenMonitor:
    def __init__(self):
        self.tokens = {
            "AKIAIOSFODNN7EXAMPLE": "AWS Access Key (Admin)",
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY": "AWS Secret Key",
            "db_password.txt": "Database Password Bait",
            "backup.sql": "Database Backup Bait"
        }

    async def check_command(self, ip, command):
        """Check if a command contains or accesses a honeytoken."""
        for token, description in self.tokens.items():
            if token in command:
                logger.warning(f"HONEYTOKEN ALERT: {description} accessed by {ip}")
                
                # Broadcast alert to UI
                await manager.broadcast({
                    "event": "HONEYTOKEN_ACCESS",
                    "ip": ip,
                    "token": description,
                    "command": command
                })

                # Telegram Alert
                send_telegram_alert(f"🚨 *CRITICAL ALERT: Honeytoken Access*\n\n*IP:* `{ip}`\n*Token:* `{description}`\n*Command:* `{command}`")
                return True
        return False

token_monitor = HoneytokenMonitor()
