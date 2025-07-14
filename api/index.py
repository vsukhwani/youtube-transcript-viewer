from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization')

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        response = {
            'status': 'success',
            'message': 'YouTube Transcript API is running',
            'api_endpoints': [
                '/api/transcript_v2',
                '/api/languages_v4'
            ],
            'timestamp': 'July 14, 2025',
            'environment': os.environ.get('VERCEL_ENV', 'development')
        }
        
        self.wfile.write(json.dumps(response).encode())
