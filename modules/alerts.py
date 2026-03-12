"""
SILA DATA HACK 2026 - Alert System
Inatoa arifa kwa njia mbalimbali
"""

import threading
import time
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class AlertSystem:
    """
    Mfumo wa Arifa - Inatoa tahadhari na taarifa
    """
    
    def __init__(self, db):
        self.db = db
        self.running = False
        self.alert_thread = None
        self.thresholds = {
            'daily_data': 1024,  # MB (1GB)
            'hourly_data': 200,   # MB
            'new_network': True,
            'low_battery': 15,    # Asilimia
            'connection_loss': True
        }
        
    def start(self):
        """Anzisha mfumo wa arifa"""
        self.running = True
        self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
        self.alert_thread.start()
        logger.info("🔔 Mfumo wa arifa umeanza")
        
    def stop(self):
        """Simamisha mfumo wa arifa"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join(timeout=5)
            
    def _alert_loop(self):
        """Kitovu cha arifa"""
        last_check = {}
        
        while self.running:
            try:
                now = datetime.now()
                
                # Angalia daily threshold
                if self.should_check('daily', last_check, 3600):  # Kila saa 1
                    self.check_daily_threshold()
                    last_check['daily'] = now
                
                # Angalia new networks
                if self.thresholds['new_network']:
                    self.check_new_networks()
                    
                # Angalia connection
                if self.thresholds['connection_loss']:
                    self.check_connection()
                    
                time.sleep(300)  # Angalia kila dakika 5
                
            except Exception as e:
                logger.error(f"Kosa katika alert loop: {e}")
                time.sleep(60)
    
    def should_check(self, key, last_check, interval):
        """Angalia kama
