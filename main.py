#!/usr/bin/env python3
"""
SILA DATA HACK 2026 - Main Launcher
Premium Edition - Inaunganisha vipengele vyote
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime

# Weka path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules zetu
from config import SYSTEM_INFO, COLLECTION_CONFIG, SERVER_CONFIG
from core.collector import DataCollector
from core.encryptor import DataEncryptor
from database.setup import init_database
from database.operations import DatabaseOperations
from server.server import start_server
from modules.whatsapp_bot import WhatsAppBot
from modules.alerts import AlertSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sila_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SilaDataHack:
    """
    Mfumo Mkuu wa SILA DATA HACK 2026
    Inasimamia modules zote
    """
    
    def __init__(self):
        self.name = SYSTEM_INFO['name']
        self.version = SYSTEM_INFO['version']
        self.running = False
        self.threads = []
        
        # Initialize components
        self.db = DatabaseOperations()
        self.encryptor = DataEncryptor()
        self.collector = DataCollector(self.db, self.encryptor)
        self.alerter = AlertSystem(self.db)
        self.bot = WhatsAppBot(self.db, self.alerter)
        
        logger.info(f"🚀 {self.name} v{self.version} inaanzishwa...")
    
    def print_banner(self):
        """Onyesha banner nzuri"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗██╗      █████╗     ██████╗  █████╗ ████████╗  ║
║   ██╔════╝██║██║     ██╔══██╗    ██╔══██╗██╔══██╗╚══██╔══╝  ║
║   ███████╗██║██║     ███████║    ██║  ██║███████║   ██║     ║
║   ╚════██║██║██║     ██╔══██║    ██║  ██║██╔══██║   ██║     ║
║   ███████║██║███████╗██║  ██║    ██████╔╝██║  ██║   ██║     ║
║   ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝     ║
║                                                              ║
║   ████████╗███████╗ ██████╗██╗  ██╗    ██████╗  █████╗     ║
║   ╚══██╔══╝██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔══██╗    ║
║      ██║   █████╗  ██║     ███████║    ██████╔╝███████║    ║
║      ██║   ██╔══╝  ██║     ██╔══██║    ██╔══██╗██╔══██║    ║
║      ██║   ███████╗╚██████╗██║  ██║    ██████╔╝██║  ██║    ║
║      ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ║
║                                                              ║
║           🚀 PREMIUM EDITION 2026 - v{self.version} 🚀           ║
║           🔥 MWENYE MAMLAKA YA DATA ZAKO 🔥                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"\n📅 Tarehe: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Mtumiaji: {os.getenv('USER', 'SILA-USER')}")
        print("=" * 70)
    
    def start_collection(self):
        """Anza kukusanya data"""
        logger.info("📡 Mkusanyaji data anaanza...")
        collection_thread = threading.Thread(
            target=self.collector.start_collecting,
            args=(COLLECTION_CONFIG['interval_seconds'],),
            daemon=True
        )
        collection_thread.start()
        self.threads.append(collection_thread)
        logger.info(f"✅ Mkusanyaji ameanza - kila sekunde {COLLECTION_CONFIG['interval_seconds']}")
    
    def start_server_thread(self):
        """Anza server"""
        logger.info(f"🌐 Server inaanza kwenye http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
        server_thread = threading.Thread(
            target=start_server,
            args=(self.db, self.encryptor),
            daemon=True
        )
        server_thread.start()
        self.threads.append(server_thread)
        logger.info("✅ Server imeanza")
    
    def start_bot(self):
        """Anza WhatsApp bot"""
        if BOT_CONFIG['enable_whatsapp']:
            logger.info("📱 WhatsApp bot inaanzishwa...")
            bot_thread = threading.Thread(
                target=self.bot.run,
                daemon=True
            )
            bot_thread.start()
            self.threads.append(bot_thread)
            logger.info("✅ WhatsApp bot imeanza")
    
    def start_auto_backup(self):
        """Anza backup otomatiki"""
        def backup_loop():
            while self.running:
                try:
                    self.db.create_backup()
                    logger.info("💾 Backup imeundwa")
                except Exception as e:
                    logger.error(f"❌ Backup imeshindikana: {e}")
                time.sleep(EXPORT_CONFIG['backup_interval_hours'] * 3600)
        
        if EXPORT_CONFIG['auto_backup']:
            backup_thread = threading.Thread(target=backup_loop, daemon=True)
            backup_thread.start()
            self.threads.append(backup_thread)
    
    def run(self):
        """Anzisha mfumo mzima"""
        self.print_banner()
        
        try:
            # Hakikisha database ipo
            init_database()
            
            self.running = True
            
            # Anzisha modules zote
            self.start_collection()
            self.start_server_thread()
            self.start_bot()
            self.start_auto_backup()
            
            logger.info("✅ MFUMO UMEANZA KIKAMILI!")
            logger.info("📊 Fungua browser: http://localhost:8080")
            logger.info("📱 Tuma 'status' kwa WhatsApp bot")
            logger.info("⏸️  Bonyeza Ctrl+C kuacha")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Mfumo unazimwa...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Kosa kubwa: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Zima mfumo salama"""
        self.running = False
        logger.info("🛑 Inazima modules zote...")
        
        # Funga database
        if hasattr(self, 'db'):
            self.db.close()
        
        # Subiri threads zote
        for thread in self.threads:
            thread.join(timeout=5)
        
        logger.info("✅ Mfumo umezimwa salama")
        logger.info("👋 Tuonane tena!")

if __name__ == "__main__":
    # Unda na anzisha mfumo
    app = SilaDataHack()
    app.run()
