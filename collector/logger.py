import sqlite3
import json
from datetime import datetime

def save_to_db(data):
    """Inahifadhi data kwenye SQLite"""
    conn = sqlite3.connect('/sdcard/Download/data.db')
    c = conn.cursor()
    
    # Unda table kama haipo
    c.execute('''CREATE TABLE IF NOT EXISTS network_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  network_name TEXT,
                  data_used REAL,
                  signal_strength TEXT,
                  extra_info TEXT)''')
    
    # Weka data
    c.execute("INSERT INTO network_data (timestamp, network_name, data_used, signal_strength, extra_info) VALUES (?, ?, ?, ?, ?)",
              (data['timestamp'], data['network'], data['data'], data['signal'], json.dumps(data['extra'])))
    
    conn.commit()
    conn.close()
