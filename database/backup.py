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
                    backup_file = backup_file.replace('.zip', '')
            
            # Aina ya backup
            if backup_file.endswith('.db'):
                # Full database
                shutil.copy2(backup_file, self.db_path)
                logger.info(f"✅ Database imerejeshwa kutoka: {backup_file}")
                
            elif backup_file.endswith('.sql'):
                # Structure only
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                with open(backup_file, 'r') as f:
                    sql_script = f.read()
                    cursor.executescript(sql_script)
                    
                conn.commit()
                conn.close()
                logger.info(f"✅ Structure imerejeshwa kutoka: {backup_file}")
                
            elif backup_file.endswith('.json'):
                # Data only
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                    
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for table, rows in backup_data.items():
                    for row in rows:
                        # Unda INSERT statement
                        columns = ', '.join(row.keys())
                        placeholders = ', '.join(['?' for _ in row])
                        query = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
                        
                        cursor.execute(query, list(row.values()))
                        
                conn.commit()
                conn.close()
                logger.info(f"✅ Data imerejeshwa kutoka: {backup_file}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Kosa katika restore_backup: {e}")
            return False
    
    def list_backups(self):
        """
        Orodhesha backups zote zilizopo
        """
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('backup_') and file.endswith('.zip'):
                    filepath = os.path.join(self.backup_dir, file)
                    stats = os.stat(filepath)
                    
                    backups.append({
                        'filename': file,
                        'size': stats.st_size,
                        'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        'type': file.split('_')[1] if '_' in file else 'unknown'
                    })
                    
            return sorted(backups, key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Kosa katika list_backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_last=10):
        """
        Futa backups za zamani, weka za mwisho tu
        """
        try:
            backups = self.list_backups()
            
            if len(backups) > keep_last:
                to_delete = backups[keep_last:]
                
                for backup in to_delete:
                    filepath = os.path.join(self.backup_dir, backup['filename'])
                    os.remove(filepath)
                    logger.info(f"🗑️ Backup imefutwa: {backup['filename']}")
                    
            return len(backups) - keep_last if len(backups) > keep_last else 0
            
        except Exception as e:
            logger.error(f"❌ Kosa katika cleanup_old_backups: {e}")
            return 0
