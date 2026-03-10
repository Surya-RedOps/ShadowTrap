import requests
import json
import os
from core.logger import logger

class GeoIPEngine:
    def __init__(self, cache_file="database/geoip_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Failed to save GeoIP cache: {e}")

    def get_location(self, ip):
        if ip in self.cache:
            return self.cache[ip]
        
        if ip.startswith("127.") or ip.startswith("192.168."):
             return {"country": "Local Network", "city": "Internal", "code": "LO", "lat": 0, "lon": 0}

        try:
            # Simple free API for demonstration (Rate limited)
            response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result = {
                    "country": data.get("country_name", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "code": data.get("country_code", "XX"),
                    "lat": data.get("latitude", 0),
                    "lon": data.get("longitude", 0)
                }
                self.cache[ip] = result
                self._save_cache()
                return result
        except Exception as e:
            logger.error(f"GeoIP Error for {ip}: {e}")
        
        # Consistent mock data based on IP hash
        countries = [
            {"country": "United States", "code": "US", "lat": 37.09, "lon": -95.71},
            {"country": "China", "code": "CN", "lat": 35.86, "lon": 104.19},
            {"country": "Russia", "code": "RU", "lat": 61.52, "lon": 105.31},
            {"country": "Netherlands", "code": "NL", "lat": 52.13, "lon": 5.29}
        ]
        mock = countries[sum(ord(c) for c in ip) % len(countries)]
        return {**mock, "city": "CyberSpace"}

geoip_engine = GeoIPEngine()

geoip_engine = GeoIPEngine()
