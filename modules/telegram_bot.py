"""
SILA DATA HACK 2026 - Telegram Bot
Inatuma taarifa kwa Telegram
"""

import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Bot ya Telegram - Inatuma taarifa na arifa
    """
    
    def __init__(self, db, alerter, token=None, chat_id=None):
        self.db = db
        self.alerter = alerter
        self.token = token
        self.chat_id = chat_id
        self.running = False
        self.bot_thread = None
        
    def run(self):
        """Anzisha bot"""
        if not self.token or not self.chat_id:
            logger.warning("Telegram bot haijasanidiwa")
            return
            
        self.running = True
        self.bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
        self.bot_thread.start()
        logger.info("📱 Telegram bot imeanza")
        
    def _bot_loop(self):
        """Kitovu cha bot"""
        import telegram
        from telegram.ext import Updater, CommandHandler
        
        try:
            # Initialize bot
            bot = telegram.Bot(token=self.token)
            updater = Updater(token=self.token, use_context=True)
            dp = updater.dispatcher
            
            # Add handlers
            dp.add_handler(CommandHandler("start", self.start_command))
            dp.add_handler(CommandHandler("status", self.status_command))
            dp.add_handler(CommandHandler("networks", self.networks_command))
            dp.add_handler(CommandHandler("today", self.today_command))
            dp.add_handler(CommandHandler("help", self.help_command))
            
            # Start bot
            updater.start_polling()
            logger.info("🤖 Telegram bot imeanza polling")
            
            # Keep running
            while self.running:
                import time
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Kosa katika telegram bot: {e}")
    
    def start_command(self, update, context):
        """Command /start"""
        update.message.reply_text(
            "🚀 *SILA DATA HACK 2026*\n\n"
            "Karibu! Ninakusaidia kufuatilia data zako.\n\n"
            "Tuma /help kuona amri.",
            parse_mode='Markdown'
        )
    
    def status_command(self, update, context):
        """Command /status"""
        stats = self.db.get_statistics()
        update.message.reply_text(
            f"📊 *HALI YA MFUMO*\n"
            f"• Hali: IMEWASHWA ✅\n"
            f"• Data leo: {stats.get('today_data', 0):.2f} MB\n"
            f"• Rekodi: {stats.get('total_entries', 0)}\n"
            f"• Mitandao: {stats.get('unique_networks', 0)}",
            parse_mode='Markdown'
        )
    
    def networks_command(self, update, context):
        """Command /networks"""
        networks = self.db.get_network_history()
        msg = "📡 *MITANDAO*\n"
        for net in networks[:10]:
            msg += f"• {net['network_name']}: {net['total_connections']}x\n"
        update.message.reply_text(msg, parse_mode='Markdown')
    
    def today_command(self, update, context):
        """Command /today"""
        today_data = self.db.get_data_by_date(datetime.now().strftime('%Y-%m-%d'))
        total = sum(d['data_used'] for d in today_data)
        update.message.reply_text(
            f"📅 Data za leo: {total:.2f} MB",
            parse_mode='Markdown'
        )
    
    def help_command(self, update, context):
        """Command /help"""
        update.message.reply_text(
            "🤖 *AMRI ZINAZOPOKELEWA*\n"
            "• /status - Hali ya mfumo\n"
            "• /networks - Mitandao iliyoonekana\n"
            "• /today - Data za leo\n"
            "• /help - Msaada huu",
            parse_mode='Markdown'
        )
    
    def send_message(self, message):
        """Tuma ujumbe kwa Telegram"""
        try:
            import telegram
            bot = telegram.Bot(token=self.token)
            bot.send_message(chat_id=self.chat_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Kosa katika send_message: {e}")
            return False
