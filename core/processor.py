"""
SILA DATA HACK 2026 - Data Processor
Inachambua na kusindika data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Mchambuzi Data - Inachambua mifumo na kutoa maarifa
    """
    
    def __init__(self, db):
        self.db = db
        self.cache = {}
        
    def analyze_daily_patterns(self, days=7):
        """Chambua mifumo ya kila siku"""
        try:
            # Pata data
            data = self.db.get_all_network_data(limit=1000)
            if not data:
                return {}
                
            # Geuza kuwa DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date
            
            # Mifumo ya saa
            hourly_usage = df.groupby('hour')['data_used'].mean().to_dict()
            
            # Siku zenye data nyingi
            daily_usage = df.groupby('date')['data_used'].sum().nlargest(5).to_dict()
            
            # Mitandao inayotumika zaidi
            top_networks = df.groupby('network_name')['data_used'].sum().nlargest(5).to_dict()
            
            return {
                'hourly_pattern': hourly_usage,
                'peak_days': {str(k): v for k, v in daily_usage.items()},
                'top_networks': top_networks,
                'average_daily': df.groupby('date')['data_used'].sum().mean(),
                'total_records': len(df),
                'date_range': {
                    'start': str(df['timestamp'].min()),
                    'end': str(df['timestamp'].max())
                }
            }
            
        except Exception as e:
            logger.error(f"Kosa katika analyze_daily_patterns: {e}")
            return {}
    
    def predict_usage(self, days_ahead=7):
        """Tabiri matumizi ya siku zijazo"""
        try:
            data = self.db.get_all_network_data(limit=500)
            if len(data) < 10:
                return {}
                
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            daily = df.groupby('date')['data_used'].sum()
            
            # Simple moving average prediction
            if len(daily) > 3:
                last_3_days = daily.tail(3).mean()
                predictions = {
                    str((datetime.now().date() + timedelta(days=i+1)).isoformat()): 
                    last_3_days * (1 + np.random.randn() * 0.1)
                    for i in range(days_ahead)
                }
                return predictions
                
        except Exception as e:
            logger.error(f"Kosa katika predict_usage: {e}")
            
        return {}
    
    def detect_anomalies(self, threshold=2.0):
        """Gundua matumizi yasiyo ya kawaida"""
        try:
            data = self.db.get_all_network_data(limit=200)
            if len(data) < 10:
                return []
                
            df = pd.DataFrame(data)
            df['data_used'] = pd.to_numeric(df['data_used'], errors='coerce')
            
            # Z-score method
            mean = df['data_used'].mean()
            std = df['data_used'].std()
            
            if std == 0:
                return []
                
            anomalies = df[np.abs(df['data_used'] - mean) > threshold * std]
            
            return anomalies.to_dict('records')
            
        except Exception as e:
            logger.error(f"Kosa katika detect_anomalies: {e}")
            return []
    
    def generate_insights(self):
        """Toa maarifa muhimu"""
        patterns = self.analyze_daily_patterns()
        anomalies = self.detect_anomalies()
        
        insights = []
        
        # Insight 1: Muda wa kilele
        if patterns.get('hourly_pattern'):
            peak_hour = max(patterns['hourly_pattern'], key=patterns['hourly_pattern'].get)
            insights.append(f"📊 Kilele cha matumizi ni saa {peak_hour}:00")
        
        # Insight 2: Mitandao
        if patterns.get('top_networks'):
            top_network = list(patterns['top_networks'].keys())[0]
            insights.append(f"📡 Mtandao unaotumika zaidi: {top_network}")
        
        # Insight 3: Anomalies
        if anomalies:
            insights.append(f"⚠️ Umegunduliwa matumizi {len(anomalies)} yasiyo ya kawaida")
        
        # Insight 4: Wastani
        if patterns.get('average_daily'):
            insights.append(f"📈 Wastani wa kila siku: {patterns['average_daily']:.2f} MB")
        
        return insights
    
    def get_network_summary(self, network_name):
        """Pata muhtasari wa mtandao maalum"""
        try:
            data = self.db.get_data_by_network(network_name, limit=100)
            if not data:
                return {}
                
            df = pd.DataFrame(data)
            df['data_used'] = pd.to_numeric(df['data_used'], errors='coerce')
            
            return {
                'name': network_name,
                'total_usage': df['data_used'].sum(),
                'average_usage': df['data_used'].mean(),
                'max_usage': df['data_used'].max(),
                'min_usage': df['data_used'].min(),
                'times_seen': len(df),
                'first_seen': df['timestamp'].iloc[-1] if len(df) > 0 else None,
                'last_seen': df['timestamp'].iloc[0] if len(df) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Kosa katika get_network_summary: {e}")
            return {}
