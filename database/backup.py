"""
SILA DATA HACK 2026 - Database Backup
Inahifadhi nakala za usalama
"""

import sqlite3
import os
import shutil
import json
import zipfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """
    Mhifadhi Nakala - Inaunda na kurejesha backup
    """
    
    def __init__(self, db_path='data/sila_data_2026.db'):
        self.db_path = db_path
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self, backup_type='full'):
        """
        Unda backup ya database
        backup_type: 'full', 'structure', 'data_only'
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if backup_type == 'full':
                # Nakili database nzima
                backup_file = os.path.join(
                    self.backup_dir, 
                    f"backup_full_{timestamp}.db"
                )
                shutil.copy2(self.db_path, backup_file)
                
                # Unda metadata
                metadata = {
                    'timestamp': timestamp,
                    'type': 'full',
                    'original_size': os.path.getsize(self.db_path),
                    'backup_size': os.path.getsize(backup_file)
                }
                
            elif backup_type == 'structure':
                # Hifadhi tu structure ya database
                backup_file = os.path.join(
                    self.backup_dir, 
                    f"backup_structure_{timestamp}.sql"
                )
                
                conn = sqlite3.connect(self.db_path)
                with open(backup_file, 'w') as f:
                    for line in conn.iterdump():
                        if line.startswith('CREATE'):
                            f.write(f'{line}\n')
                conn.close()
                
            elif backup_type == 'data_only':
                # Hifadhi data tu kama JSON
                backup_file = os.path.join(
                    self.backup_dir, 
                    f"backup_data_{timestamp}.json"
                )
                
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Pata data kutoka tables zote
                backup_data = {}
                tables = ['network_data', 'daily_summary', 'networks_history']
                
                for table in tables:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    backup_data[table] = [dict(row) for row in rows]
                    
                conn.close()
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, default=str)
                    
            # Compress backup
            if backup_file.endswith(('.db', '.sql', '.json')):
                with zipfile.ZipFile(f"{backup_file}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(backup_file, os.path.basename(backup_file))
                os.remove(backup_file)
                backup_file = f"{backup_file}.zip"
            
            logger.info(f"✅ Backup imeundwa: {backup_file}")
            
            # Safisha backups za zamani
            self.cleanup_old_backups()
            
            return backup_file
            
        except Exception as e:
            logger.error(f"❌ Kosa katika create_backup: {e}")
            return None
    
    def restore_backup(self, backup_file):
        """
        Rejesha database kutoka kwenye backup
        """
        try:
            if not os.path.exists(backup_file):
                logger.error(f"Backup haipo: {backup_file}")
                return False
                
            # Extract kama ni zip
            if backup_file.endswith('.zip'):
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(self.backup_dir)
                    backup_file = backup_file
