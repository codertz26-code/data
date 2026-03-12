"""
SILA DATA HACK 2026 - WhatsApp Bot
Inatuma taarifa kwa WhatsApp
"""

import time
import threading
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class WhatsAppBot:
    """
    Bot ya WhatsApp - Inatuma taarifa na arifa
    """
    
    def __init__(self, db, alerter, phone_number="+255650034217"):
        self.db = db
        self.alerter = alerter
        self.phone_number = phone_number
        self.running = False
        self.bot_thread = None
        
        # Kwa sasa tunatumia Twilio (utahitaji account)
        # Au unaweza kutumia whatsapp-web.js via subprocess
        self.twilio_account = None
        self.twilio_token = None
        
    def run(self):
        """Anzisha bot"""
        self.running = True
        self.bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
        self.bot_thread.start()
        logger.info("📱 WhatsApp bot imeanza")
        
    def _bot_loop(self):
        """Kitovu cha bot"""
        last_report = None
        
        while self.running:
            try:
                now = datetime.now()
                
                # Tuma ripoti ya kila siku saa 8 mchana
                if now.hour == 20 and (last_report is None or last_report.date() != now.date()):
                    self.send_daily_report()
                    last_report = now
                    
                # Angalia thresholds
                self.check_thresholds()
                
                # Angalia messages (kwa sasa ni placeholder)
                # Hapa uta-add functionality ya kupokea messages
                
                time.sleep(60)  # Angalia kila dakika
                
            except Exception as e:
                logger.error(f"Kosa katika bot loop: {e}")
                time.sleep(300)  # Subiri dakika 5 kama kuna error
    
    def send_message(self, message):
        """
        Tuma ujumba kwa WhatsApp
        """
        try:
            # Hapa utaweka actual WhatsApp API
            # Kwa sasa tunaandika kwenye log tu
            logger.info(f"📱 WhatsApp: {message}")
            
            # Placeholder kwa ajili ya Twilio
            if self.twilio_account and self.twilio_token:
                # Twilio code itakuja hapa
                pass
                
            return True
            
        except Exception as e:
            logger.error(f"Kosa katika send_message: {e}")
            return False
    
    def send_daily_report(self):
        """
        Tuma ripoti ya kila siku
        """
        try:
            # Pata statistics
            stats = self.db.get_statistics()
            
            # Pata data za leo
            today = datetime.now().strftime('%Y-%m-%d')
            today_data = self.db.get_data_by_date(today)
            today_total = sum(d['data_used'] for d in today_data)
            
            # Pata mitandao
            networks = self.db.get_network_history()
            
            # Unda message
            message = f"""
📊 *RIPOTI YA SILA DATA HACK - {today}*

📈 *MUHTASARI WA LEO*
• Data iliyotumika: {today_total:.2f} MB
• Mara za kukusanya: {len(today_data)}
• Mitandao tofauti: {len(networks)}

📡 *MITANDAO INAYOTUMIKA*
"""
            # Ongeza top 5 networks
            for net in networks[:5]:
                message += f"• {net['network_name']}: {net['total_connections']} mara\n"
                
            message += f"""
📊 *TAKWIMU ZA JUMLA*
• Jumla ya data: {stats.get('total_data', 0):.2f} MB
• Jumla ya rekodi: {stats.get('total_entries', 0)}
• Tangu: {stats.get('first_date', 'Unknown')}

🚀 *SILA DATA HACK 2026*
            """
            
            # Tuma message
            self.send_message(message)
            logger.info("✅ Ripoti ya kila siku imetumwa")
            
        except Exception as e:
            logger.error(f"Kosa katika send_daily_report: {e}")
    
    def check_thresholds(self):
        """
        Angalia kama data imefikia kiwango fulani
        """
        try:
            stats = self.db.get_statistics()
            today_data = stats.get('today_data', 0)
            
            # Angalia kama imefikia GB 1 (1024 MB)
            if today_data > 1024:
                self.send_message(
                    f"⚠️ *TAHADHARI*\n"
                    f"Umefikia {today_data:.2f} MB leo!\n"
                    f"Tafadhali angalia matumizi yako."
                )
                
        except Exception as e:
            logger.error(f"Kosa katika check_thresholds: {e}")
    
    def handle_command(self, command):
        """
        Shughulikia amri kutoka kwa mtumiaji
        """
        command = command.lower().strip()
        
        if command == 'status':
            stats = self.db.get_statistics()
            return f"""
📊 *HALI YA MFUMO*
• Hali: IMEWASHWA ✅
• Data leo: {stats.get('today_data', 0):.2f} MB
• Rekodi: {stats.get('total_entries', 0)}
• Mitandao: {stats.get('unique_networks', 0)}
            """
            
        elif command == 'networks':
            networks = self.db.get_network_history()
            msg = "📡 *MITANDAO*\n"
            for net in networks[:10]:
                msg += f"• {net['network_name']}: {net['total_connections']}x\n"
            return msg
            
        elif command == 'help':
            return """
🤖 *AMRI ZINAZOPOKELEWA*
• status - Hali ya mfumo
• networks - Mitandao iliyoonekana
• today - Data za leo
• backup - Unda backup
• help - Msaada huu
            """
            
        elif command == 'today':
            today_data = self.db.get_data_by_date(datetime.now().strftime('%Y-%m-%d'))
            total = sum(d['data_used'] for d in today_data)
            return f"📅 Data za leo: {total:.2f} MB"
            
        else:
            return "❌ Amri haitambuliki. Tuma 'help' kuona orodha."
