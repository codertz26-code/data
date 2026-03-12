"""
SILA DATA HACK 2026 - Database Setup
Inaunda database na tables
"""

import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join('data', 'sila_data_2026.db')

def init_database():
    """
    Inaunda database na tables zote muhimu
    """
    try:
        # Hakikisha folder ipo
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Unganisha kwenye database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table ya network data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                network_name TEXT,
                data_used REAL DEFAULT 0,
                signal_strength TEXT,
                connection_type TEXT DEFAULT 'wifi',
                ip_address TEXT,
                upload_speed REAL DEFAULT 0,
                download_speed REAL DEFAULT 0,
                extra_info TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table ya daily summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_data REAL DEFAULT 0,
                avg_signal TEXT,
                most_used_network TEXT,
                entries_count INTEGER DEFAULT 0,
                peak_hour INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table ya network history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network_name TEXT UNIQUE NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                total_connections INTEGER DEFAULT 1,
                avg_strength TEXT,
                total_data REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table ya system events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_description TEXT,
                event_data TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table ya users (kwa ajili ya usalama)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                last_login TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Unda indexes kwa ajili ya speed
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON network_data(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_network ON network_data(network_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON daily_summary(date)')
        
        conn.commit()
        
        # Ingiza default admin user kama haipo
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            import hashlib
            default_password = "Sila@2026Admin"
            password_hash = hashlib.sha256(default_password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ('admin', password_hash, 'admin'))
            conn.commit()
            
        conn.close()
        
        logger.info(f"✅ Database imeundwa: {DB_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Kosa katika init_database: {e}")
        return False

def get_connection():
    """
    Rudisha connection kwenye database
    """
    try:
        # Hakikisha database ipo
        if not os.path.exists(DB_PATH):
            init_database()
            
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Rudisha rows kama dictionaries
        return conn
        
    except Exception as e:
        logger.error(f"❌ Kosa katika get_connection: {e}")
        return None
