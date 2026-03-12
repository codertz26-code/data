"""
SILA DATA HACK 2026 - Configuration Premium
"""

import os
from datetime import datetime

# ============================================
# MFUMO MSINGI
# ============================================
VERSION = "2026.1.0"
RELEASE_DATE = "2026-03-12"
AUTHOR = "SILA TECH"
PROJECT_NAME = "SILA DATA HACK"

# ============================================
# MAHALI PA DATA
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "sila_data_2026.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Unda folders kama hazipo
for folder in [DATA_DIR, BACKUP_DIR, LOG_DIR]:
    os.makedirs(folder, exist_ok=True)

# ============================================
# MIPANGILIO YA UKUSANYAJI DATA
# ============================================
COLLECTION_CONFIG = {
    "interval_seconds": 30,           # Kukusanya kila sekunde 30
    "collect_wifi": True,              # Kukusanya data za Wi-Fi
    "collect_mobile": True,             # Kukusanya data za mobile
    "collect_location": False,          # Mahali (hiari)
    "collect_battery": True,            # Betri ya simu
    "collect_apps": False,              # Apps zinazotumia data
    "max_records_per_day": 10000,       # Rekodi za juu kwa siku
    "auto_clean_days": 90,              # Futa data za zamani baada ya siku 90
}

# ============================================
# USALAMA WA JUU
# ============================================
SECURITY_CONFIG = {
    "encryption_enabled": True,          # Fungasha data kwa siri
    "encryption_key": "SILA-SECRET-KEY-2026",  # Badilisha hii!
    "require_auth": True,                 # Hitaji nenosiri
    "master_password": "Sila@2026Admin",   # Nenosiri kuu
    "session_timeout": 3600,               # Kikao kinamalizika baada ya saa 1
    "max_login_attempts": 5,                # Jaribio la juu la kuingia
}

# ============================================
# SERVER NA DASHBOARD
# ============================================
SERVER_CONFIG = {
    "host": "localhost",
    "port": 8080,
    "debug": False,
    "dashboard_title": "SILA DATA HACK 2026",
    "theme": "dark",                       # Nyeusi premium
    "refresh_interval": 10,                 # Dashboard inaburudisha kila sekunde 10
    "allow_remote_access": False,           # Ruhusu access kutoka nje (Tahadhari!)
}

# ============================================
# INTEGRATION NA BOTS
# ============================================
BOT_CONFIG = {
    "enable_whatsapp": True,
    "whatsapp_number": "+255XXXXXXXXX",     # Namba yako ya WhatsApp
    "enable_telegram": False,
    "telegram_token": "YOUR_TOKEN_HERE",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "daily_report_time": "20:00",            # Ripoti ya kila siku saa 8 mchana
    "alert_on_threshold": True,               # Arifa data ikifikia kiwango
    "data_threshold_mb": 1000,                # Arifa baada ya MB 1000
}

# ============================================
# THUMANI ZA DASHBOARD
# ============================================
CHART_CONFIG = {
    "primary_color": "#0066FF",           # Blue premium
    "secondary_color": "#00CCFF",          # Light blue
    "background_color": "#0A0A0A",         # Black premium
    "card_bg_color": "#1E1E1E",            # Dark gray
    "text_color": "#FFFFFF",                # White
    "danger_color": "#FF4444",              # Red
    "success_color": "#00C851",              # Green
    "warning_color": "#FFBB33",               # Yellow
}

# ============================================
# EXPORT NA BACKUP
# ============================================
EXPORT_CONFIG = {
    "auto_backup": True,
    "backup_interval_hours": 24,            # Backup kila saa 24
    "backup_format": "encrypted",            # Encrypted au plain
    "export_formats": ["json", "csv", "excel", "pdf"],
    "max_backups_keep": 10,                  # Weka backup 10 za mwisho
}

# ============================================
# MAPITO YA MFUMO
# ============================================
SYSTEM_INFO = {
    "name": PROJECT_NAME,
    "version": VERSION,
    "release": RELEASE_DATE,
    "author": AUTHOR,
    "status": "PREMIUM",
    "license": "PRIVATE - SILA TECH",
    "environment": "PRODUCTION"
}
