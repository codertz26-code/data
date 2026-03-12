from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from urllib.parse import parse_qs, urlparse

class DataHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            # Serve dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('/sdcard/Download/dashboard/index.html', 'r') as f:
                self.wfile.write(f.read().encode())
                
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            
            with open('/sdcard/Download/dashboard/style.css', 'r') as f:
                self.wfile.write(f.read().encode())
                
        elif self.path == '/script.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            
            with open('/sdcard/Download/dashboard/script.js', 'r') as f:
                self.wfile.write(f.read().encode())
                
        elif self.path.startswith('/api/data'):
            # Return data from database
            conn = sqlite3.connect('/sdcard/Download/data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM network_data ORDER BY timestamp DESC LIMIT 50")
            rows = c.fetchall()
            conn.close()
            
            # Convert to JSON
            data = []
            for row in rows:
                data.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'network': row[2],
                    'data': row[3],
                    'signal': row[4]
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        else:
            self.send_response(404)
            self.end_headers()

def run():
    port = 8080
    server = HTTPServer(('localhost', port), DataHandler)
    print(f"🌐 Server imeanza kwenye http://localhost:{port}")
    print("📱 Fungua browser na uweke anwani hiyo")
    server.serve_forever()

if __name__ == '__main__':
    run()
