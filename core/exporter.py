"""
SILA DATA HACK 2026 - Data Exporter
Inahamisha data kwa formats mbalimbali
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os
import logging
import pdfkit
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

class DataExporter:
    """
    Kihamishaji Data - Inahamisha data kwa CSV, Excel, PDF, JSON
    """
    
    def __init__(self, db, encryptor=None):
        self.db = db
        self.encryptor = encryptor
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_to_json(self, data=None, filename=None):
        """Hamisha data kuwa JSON"""
        try:
            if data is None:
                data = self.db.get_all_network_data(limit=1000)
                
            if filename is None:
                filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✅ JSON imehifadhiwa: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Kosa katika export_to_json: {e}")
            return None
    
    def export_to_csv(self, data=None, filename=None):
        """Hamisha data kuwa CSV"""
        try:
            if data is None:
                data = self.db.get_all_network_data(limit=1000)
                
            if not data:
                return None
                
            if filename is None:
                filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
            filepath = os.path.join(self.export_dir, filename)
            
            # Andika CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Andika headers
                headers = data[0].keys()
                writer.writerow(headers)
                
                # Andika data
                for row in data:
                    writer.writerow([row.get(h, '') for h in headers])
                    
            logger.info(f"✅ CSV imehifadhiwa: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Kosa katika export_to_csv: {e}")
            return None
    
    def export_to_excel(self, data=None, filename=None):
        """Hamisha data kuwa Excel"""
        try:
            if data is None:
                data = self.db.get_all_network_data(limit=1000)
                
            if not data:
                return None
                
            if filename is None:
                filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
            filepath = os.path.join(self.export_dir, filename)
            
            # Geuza kuwa DataFrame
            df = pd.DataFrame(data)
            
            # Andika Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Rekebisha upana wa columns
                worksheet = writer.sheets['Data']
                for column in df:
                    column_length = max(df[column].astype(str).map(len).max(), len(column))
                    column_length = min(column_length, 50)
                    worksheet.column_dimensions[column].width = column_length + 2
                    
            logger.info(f"✅ Excel imehifadhiwa: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Kosa katika export_to_excel: {e}")
            return None
    
    def export_to_pdf(self, data=None, filename=None):
        """Hamisha data kuwa PDF"""
        try:
            if data is None:
                data = self.db.get_all_network_data(limit=100)
                
            if not data:
                return None
                
            if filename is None:
                filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
            filepath = os.path.join(self.export_dir, filename)
            
            # Unda PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading_style = styles['Heading2']
            
            # Title
            title = Paragraph("SILA DATA HACK 2026 - Ripoti ya Data", title_style)
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Date
            date_str = f"Ripoti ya: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date = Paragraph(date_str, styles['Normal'])
            story.append(date)
            story.append(Spacer(1, 0.3*inch))
            
            # Statistics
            stats = self.db.get_statistics()
            stats_text = f"""
            <b>Takwimu za Jumla:</b><br/>
            Jumla ya Data: {stats.get('total_data', 0):.2f} MB<br/>
            Rekodi: {stats.get('total_entries', 0)}<br/>
            Mitandao: {stats.get('unique_networks', 0)}<br/>
            Data za Leo: {stats.get('today_data', 0):.2f} MB
            """
            stats_para = Paragraph(stats_text, styles['Normal'])
            story.append(stats_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Data Table
            if data:
                # Prepare table data
                table_data = [['Muda', 'Mtandao', 'Data (MB)', 'Ishara']]
                for row in data[:50]:  # Limit to 50 rows
                    table_data.append([
                        row.get('timestamp', '')[:19],
                        row.get('network_name', ''),
                        f"{row.get('data_used', 0):.2f}",
                        row.get('signal_strength', '')
                    ])
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"✅ PDF imehifadhiwa: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Kosa katika export_to_pdf: {e}")
            return None
    
    def export_all_formats(self, data=None):
        """Hamisha kwa formats zote"""
        results = {}
        
        results['json'] = self.export_to_json(data)
        results['csv'] = self.export_to_csv(data)
        results['excel'] = self.export_to_excel(data)
        results['pdf'] = self.export_to_pdf(data)
        
        return results
