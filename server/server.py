"""
SILA DATA HACK 2026 - HTTP Server
Inatoa API na dashboard
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys
import logging
from datetime import datetime

# Ongeza path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.operations import DatabaseOperations
from server.api import APIEndpoints
from server.auth import Authentication

logger = logging.getLogger(__name__)

class DataCollectorHandler(BaseHTTPRequestHandler):
    """
    Mshughulikiaji HTTP - Inashughulikia maombi yote
    """
    
    def __init__(self, *args, **kwargs):
        self.db = DatabaseOperations()
        self.api = APIEndpoints(self.db)
        self.auth = Authentication()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Shughulikia maombi ya GET"""
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)
            
            # Serve dashboard
            if path == '/' or path == '/index.html':
                self.serve_dashboard()
                
            # API endpoints
            elif path.startswith('/api/'):
                self.handle_api_request('GET', path, query)
                
            # Static files
            elif path.endswith('.css') or path.endswith('.js'):
                self.serve_static_file(path)
                
            else:
                self.send_error(404, "File haipo")
                
        except Exception as e:
            logger.error(f"Kosa katika GET: {e}")
            self.send_error(500, f"Internal Error: {str(e)}")
            
        finally:
            self.db.close()
    
    def do_POST(self):
        """Shughulikia maombi ya POST"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
            
            if self.path.startswith('/api/'):
                self.handle_api_request('POST', self.path, data)
            else:
                self.send_error(404, "API haipo")
                
        except Exception as e:
            logger.error(f"Kosa katika POST: {e}")
            self.send_error(500, f"Internal Error: {str(e)}")
            
        finally:
            self.db.close()
    
    def handle_api_request(self, method, path, data):
        """Shughulikia maombi ya API"""
        
        # Check authentication
        auth_header = self.headers.get('Authorization', '')
        if not self.auth.verify_token(auth_header):
            self.send_json_response(401, {'error': 'Haijathibitishwa'})
            return
        
        # Route requests
        if method == 'GET':
            if path == '/api/data':
                result = self.api.get_data(data)
                self.send_json_response(200, result)
                
            elif path == '/api/stats':
                result = self.api.get_statistics()
                self.send_json_response(200, result)
                
            elif path == '/api/networks':
                result = self.api.get_networks()
                self.send_json_response(200, result)
                
            elif path == '/api/today':
                result = self.api.get_today_data()
                self.send_json_response(200, result)
                
            elif path == '/api/summaries':
                result = self.api.get_daily_summaries(data)
                self.send_json_response(200, result)
                
            elif path.startswith('/api/network/'):
                network = path.replace('/api/network/', '')
                result = self.api.get_network_data(network, data)
                self.send_json_response(200, result)
                
            else:
                self.send_json_response(404, {'error': 'API haipo'})
                
        elif method == 'POST':
            if path == '/api/data':
                result = self.api.insert_data(data)
                self.send_json_response(201, result)
                
            elif path == '/api/backup':
                result = self.api.create_backup()
                self.send_json_response(200, result)
                
            elif path == '/api/export':
                result = self.api.export_data(data)
                self.send_json_response(200, result)
                
            elif path == '/api/analyze':
                result = self.api.analyze_data(data)
                self.send_json_response(200, result)
                
            else:
                self.send_json_response(404, {'error': 'API haipo'})
    
    def serve_dashboard(self):
        """Toa dashboard HTML"""
        try:
            dashboard_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'dashboard', 'index.html'
            )
            
            if os.path.exists(dashboard_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                with open(dashboard_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Dashboard haipo")
                
        except Exception as e:
            logger.error(f"Kosa katika serve_dashboard: {e}")
            self.send_error(500, "Internal error")
    
    def serve_static_file(self, path):
        """Toa static files (CSS, JS)"""
        try:
            # Kwa sasa, CSS na JS ziko ndani ya HTML
            self.send_error(404, "Static files hazipo")
            
        except Exception as e:
            logger.error(f"Kosa katika serve_static: {e}")
            self.send_error(500, "Internal error")
    
    def send_json_response(self, status_code, data):
        """Tuma JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, default=str, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override log_message"""
        logger.info(f"{self.address_string()} - {format % args}")

def start_server(db=None, encryptor=None, host='localhost', port=8080):
    """
    Anzisha HTTP server
    """
    try:
        server = HTTPServer((host, port), DataCollectorHandler)
        logger.info(f"🌐 Server imeanza kwenye http://{host}:{port}")
        logger.info("📊 Fungua browser kuona dashboard")
        
        # Keep server running
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("👋 Server imezimwa")
        server.shutdown()
    except Exception as e:
        logger.error(f"❌ Kosa katika server: {e}")
