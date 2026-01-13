import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional

class IndicatorCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_path(self, symbol: str) -> str:
        return os.path.join(self.cache_dir, f"{symbol}_indicators.json")
        
    def get(self, symbol: str) -> Optional[Dict]:
        """Get cached indicators if they exist and are fresh (less than 1 day old)"""
        cache_path = self._get_cache_path(symbol)
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            # Check if cache is fresh (less than 1 day old)
            cache_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cache_time > timedelta(days=1):
                return None
                
            return data['indicators']
        except Exception:
            return None
            
    def set(self, symbol: str, indicators: Dict) -> None:
        """Cache indicators for a symbol"""
        cache_path = self._get_cache_path(symbol)
        data = {
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception:
            # If caching fails, just log and continue
            pass