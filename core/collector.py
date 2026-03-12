"""
SILA DATA HACK 2026 - Data Collector
Inakusanya data za mtandao na mfumo
"""

import os
import time
import json
import subprocess
import threading
from datetime import datetime
import logging
import psutil
import netifaces

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Mkusanyaji Data - Inakusanya taarifa za mtandao, betri, na mfumo
    """
    
    def __init__(self, db, encryptor=None):
        self.db = db
        self.encryptor = encryptor
        self.running = False
        self.collection_thread = None
        self.stats = {
            'collected': 0,
            'failed': 0,
            'last_collection': None
        }
        
    def start_collecting(self, interval_seconds=30):
        """Anza mchakato wa kukusanya data"""
        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.collection_thread.start()
        logger.info(f"📡 Mkusanyaji ameanza - kila sekunde {interval_seconds}")
        
    def stop_collecting(self):
        """Simamisha ukusanyaji"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("📡 Mkusanyaji amesimama")
        
    def _collection_loop(self, interval):
        """Kitovu cha ukusanyaji - inaendeshwa na thread"""
        while self.running:
            try:
                # Kukusanya data
                data = self.collect_all_data()
                
                # Kuweka kwenye database
                if data:
                    self.db.insert_network_data(data)
                    self.stats['collected'] += 1
                    self.stats['last_collection'] = datetime.now()
                    
                    # Sasisha daily summary
                    self.db.update_daily_summary()
                    
                    # Sasisha network history
                    if data.get('network_name'):
                        self.db.update_network_history(
                            data['network_name'],
                            data.get('signal_strength', 'unknown')
                        )
                    
                    logger.debug(f"Data imekusanywa: {data['network_name']}")
                    
            except Exception as e:
                self.stats['failed'] += 1
                logger.error(f"Kosa katika ukusanyaji: {e}")
                
            # Subiri kabla ya kukusanya tena
            time.sleep(interval)
    
    def collect_all_data(self):
        """Kusanya data zote kwa wakati mmoja"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'network_name': self.get_current_network(),
                'data_used': self.get_data_usage(),
                'signal_strength': self.get_signal_strength(),
                'connection_type': self.get_connection_type(),
                'ip_address': self.get_ip_address(),
                'upload_speed': self.get_upload_speed(),
                'download_speed': self.get_download_speed(),
                'extra_info': {
                    'battery': self.get_battery_info(),
                    'system': self.get_system_info(),
                    'location': self.get_location()  # Optional
                }
            }
            
            # Encrypt data if enabled
            if self.encryptor and self.encryptor.enabled:
                data = self.encryptor.encrypt_data(data)
                
            return data
            
        except Exception as e:
            logger.error(f"Kosa katika collect_all_data: {e}")
            return None
    
    def get_current_network(self):
        """Pata jina la mtandao uliounganishwa"""
        try:
            # Jaribu Termux API kwanza (kwa simu)
            result = subprocess.run(
                ['termux-wifi-connection'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('ssid', 'unknown')
        except:
            pass
            
        try:
            # Backup method kwa PC
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                if iface.startswith(('wlan', 'eth')):
                    return iface
        except:
            pass
            
        return 'unknown'
    
    def get_data_usage(self):
        """Pata matumizi ya data kwa sekunde"""
        try:
            # Tumia psutil kupata network stats
            net_io = psutil.net_io_counters()
            # Rudisha random small value kwa sasa (utaimplement vizuri baadaye)
            return round(net_io.bytes_recv / (1024 * 1024), 2)  # MB
        except:
            return 0.0
    
    def get_signal_strength(self):
        """Pata nguvu ya ishara"""
        try:
            result = subprocess.run(
                ['termux-wifi-scaninfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                scans = json.loads(result.stdout)
                if scans:
                    return str(scans[0].get('rssi', 'unknown'))
        except:
            pass
        return 'unknown'
    
    def get_connection_type(self):
        """Pata aina ya muunganisho"""
        try:
            if self.get_current_network() != 'unknown':
                return 'wifi'
            # Angalia kama ni mobile data
            return 'mobile'
        except:
            return 'unknown'
    
    def get_ip_address(self):
        """Pata anwani ya IP"""
        try:
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0].get('addr', '')
        except:
            pass
        return ''
    
    def get_upload_speed(self):
        """Pata kasi ya upload (approximate)"""
        # Hii inahitaji implementation maalum
        return 0.0
    
    def get_download_speed(self):
        """Pata kasi ya download (approximate)"""
        # Hii inahitaji implementation maalum
        return 0.0
    
    def get_battery_info(self):
        """Pata taarifa za betri"""
        try:
            result = subprocess.run(
                ['termux-battery-status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
            
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percentage': battery.percent,
                    'plugged': battery.power_plugged
                }
        except:
            pass
            
        return {}
    
    def get_system_info(self):
        """Pata taarifa za mfumo"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }
    
    def get_location(self):
        """Pata mahali (optional - inahitaji GPS)"""
        try:
            result = subprocess.run(
                ['termux-location'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return {}
    
    def get_stats(self):
        """Pata takwimu za mkusanyaji"""
        return self.stats
