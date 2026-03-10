import json
import requests
from core.logger import logger
from config.settings import NODE_ID

class NodeDistributor:
    def __init__(self, collector_url="http://central-collector:8000/api/collect"):
        self.collector_url = collector_url

    async def forward_log(self, log_data):
        """Forward a honeypot log to the central collector."""
        log_data["node_id"] = NODE_ID
        try:
            # For this implementation, we simulate an HTTP POST to a central collector
            # In a real environment, this could be a Redis message or Kafka stream
            # requests.post(self.collector_url, json=log_data, timeout=2)
            logger.debug(f"NODE_FORWARD: {log_data['ip']} -> Central Collector")
        except Exception as e:
            logger.error(f"Failed to forward log: {e}")

node_distributor = NodeDistributor()
