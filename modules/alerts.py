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
        """Angalia kama muda wa kuangalia umefika"""
        if key not in last_check:
            return True
        elapsed = (datetime.now() - last_check[key]).total_seconds()
        return elapsed >= interval
    
    def check_daily_threshold(self):
        """Angalia kama data ya leo imezidi kiwango"""
        try:
            stats = self.db.get_statistics()
            today_data = stats.get('today_data', 0)
            
            if today_data > self.thresholds['daily_data']:
                self.trigger_alert(
                    'daily_threshold',
                    f"⚠️ Umefikia {today_data:.2f} MB leo! (Kiwango: {self.thresholds['daily_data']} MB)"
                )
                
        except Exception as e:
            logger.error(f"Kosa katika check_daily_threshold: {e}")
    
    def check_new_networks(self):
        """Angalia mitandao mipya"""
        try:
            # Pata networks za saa 24 zilizopita
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            # Hii inahitaji query maalum kwenye database
            # Kwa sasa tunaacha placeholder
            pass
            
        except Exception as e:
            logger.error(f"Kosa katika check_new_networks: {e}")
    
    def check_connection(self):
        """Angalia kama mtandao umekatika"""
        try:
            # Pata data ya dakika 5 zilizopita
            five_mins_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            # Angalia kama kuna data
            # Hii inahitaji query maalum
            pass
            
        except Exception as e:
            logger.error(f"Kosa katika check_connection: {e}")
    
    def trigger_alert(self, alert_type, message, severity='info'):
        """
        Toa arifa
        """
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            # Andika kwenye log
            if severity == 'error':
                logger.error(f"🔴 ARIFA: {message}")
            elif severity == 'warning':
                logger.warning(f"🟠 ARIFA: {message}")
            else:
                logger.info(f"🔵 ARIFA: {message}")
            
            # Hifadhi kwenye database
            self.save_alert(alert_data)
            
            # Tuma kwa bots
            self.send_to_bots(alert_data)
            
            # Onyesha kwenye terminal
            self.show_notification(alert_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Kosa katika trigger_alert: {e}")
            return False
    
    def save_alert(self, alert_data):
        """Hifadhi arifa kwenye database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_events 
                (event_type, event_description, event_data)
                VALUES (?, ?, ?)
            ''', (
                alert_data['type'],
                alert_data['message'],
                json.dumps(alert_data)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Kosa katika save_alert: {e}")
    
    def send_to_bots(self, alert_data):
        """Tuma arifa kwa bots"""
        # Hii itaunganishwa na WhatsApp na Telegram bots
        pass
    
    def show_notification(self, alert_data):
        """Onyesha arifa kwenye terminal"""
        try:
            # Kwa Termux
            import subprocess
            subprocess.run([
                'termux-notification',
                '--title', f"SILA ALERT: {alert_data['type']}",
                '--content', alert_data['message'][:100]
            ])
        except:
            pass
