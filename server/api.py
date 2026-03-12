"""
SILA DATA HACK 2026 - API Endpoints
VIPI vya API
"""

import json
from datetime import datetime, timedelta
import logging

from core.processor import DataProcessor
from core.exporter import DataExporter
from database.backup import DatabaseBackup

logger = logging.getLogger(__name__)

class APIEndpoints:
    """
    API Endpoints zote za mfumo
    """
    
    def __init__(self, db):
        self.db = db
        self.processor = DataProcessor(db)
        self.exporter = DataExporter(db)
        self.backup = DatabaseBackup()
        
    def get_data(self, params):
        """
        GET /api/data
        Pata data za mtandao
        """
        try:
            limit = int(params.get('limit', [50])[0])
            offset = int(params.get('offset', [0])[0])
            
            data = self.db.get_all_network_data(limit=limit, offset=offset)
            
            return {
                'success': True,
                'count': len(data),
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_data: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_statistics(self):
        """
        GET /api/stats
        Pata takwimu za jumla
        """
        try:
            stats = self.db.get_statistics()
            
            # Ongeza insights
            insights = self.processor.generate_insights()
            
            return {
                'success': True,
                'stats': stats,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_statistics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_networks(self):
        """
        GET /api/networks
        Pata mitandao yote iliyowahi kuonekana
        """
        try:
            networks = self.db.get_network_history()
            
            result = []
            for net in networks:
                result.append({
                    'name': net['network_name'],
                    'first_seen': net['first_seen'],
                    'last_seen': net['last_seen'],
                    'total_connections': net['total_connections'],
                    'avg_strength': net['avg_strength']
                })
                
            return {
                'success': True,
                'count': len(result),
                'networks': result
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_networks: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_today_data(self):
        """
        GET /api/today
        Pata data za leo
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            data = self.db.get_data_by_date(today)
            
            total = sum(d['data_used'] for d in data)
            
            return {
                'success': True,
                'date': today,
                'count': len(data),
                'total_data': total,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_today_data: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_daily_summaries(self, params):
        """
        GET /api/summaries
        Pata muhtasari wa kila siku
        """
        try:
            days = int(params.get('days', [30])[0])
            summaries = self.db.get_daily_summaries(days)
            
            return {
                'success': True,
                'days': days,
                'summaries': summaries
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_daily_summaries: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_network_data(self, network_name, params):
        """
        GET /api/network/{name}
        Pata data za mtandao maalum
        """
        try:
            limit = int(params.get('limit', [100])[0])
            data = self.db.get_data_by_network(network_name, limit)
            
            # Pia pata summary
            summary = self.processor.get_network_summary(network_name)
            
            return {
                'success': True,
                'network': network_name,
                'count': len(data),
                'summary': summary,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_network_data: {e}")
            return {'success': False, 'error': str(e)}
    
    def insert_data(self, data):
        """
        POST /api/data
        Ingiza data mpya
        """
        try:
            # Validate data
            required_fields = ['timestamp', 'network_name']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'{field} inahitajika'}
            
            # Insert
            record_id = self.db.insert_network_data(data)
            
            # Update daily summary
            self.db.update_daily_summary()
            
            return {
                'success': True,
                'id': record_id,
                'message': 'Data imeingizwa'
            }
            
        except Exception as e:
            logger.error(f"Kosa katika insert_data: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_backup(self):
        """
        POST /api/backup
        Unda backup ya database
        """
        try:
            backup_file = self.backup.create_backup('full')
            
            if backup_file:
                return {
                    'success': True,
                    'backup_file': backup_file,
                    'message': 'Backup imeundwa'
                }
            else:
                return {'success': False, 'error': 'Backup imeshindikana'}
                
        except Exception as e:
            logger.error(f"Kosa katika create_backup: {e}")
            return {'success': False, 'error': str(e)}
    
    def export_data(self, params):
        """
        POST /api/export
        Hamisha data kwa format maalum
        """
        try:
            format_type = params.get('format', 'json')
            limit = params.get('limit', 1000)
            
            # Pata data
            data = self.db.get_all_network_data(limit=limit)
            
            # Export
            if format_type == 'json':
                filepath = self.exporter.export_to_json(data)
            elif format_type == 'csv':
                filepath = self.exporter.export_to_csv(data)
            elif format_type == 'excel':
                filepath = self.exporter.export_to_excel(data)
            elif format_type == 'pdf':
                filepath = self.exporter.export_to_pdf(data)
            else:
                return {'success': False, 'error': 'Format haitambuliki'}
            
            if filepath:
                return {
                    'success': True,
                    'file': filepath,
                    'format': format_type,
                    'message': f'Data imehifadhiwa kama {format_type}'
                }
            else:
                return {'success': False, 'error': 'Export imeshindikana'}
                
        except Exception as e:
            logger.error(f"Kosa katika export_data: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_data(self, params):
        """
        POST /api/analyze
        Chambua data kwa namna mbalimbali
        """
        try:
            analysis_type = params.get('type', 'patterns')
            
            if analysis_type == 'patterns':
                result = self.processor.analyze_daily_patterns()
            elif analysis_type == 'predict':
                days = params.get('days', 7)
                result = self.processor.predict_usage(days)
            elif analysis_type == 'anomalies':
                result = self.processor.detect_anomalies()
            elif analysis_type == 'insights':
                result = self.processor.generate_insights()
            else:
                return {'success': False, 'error': 'Aina ya analysis haipo'}
            
            return {
                'success': True,
                'type': analysis_type,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Kosa katika analyze_data: {e}")
            return {'success': False, 'error': str(e)}
