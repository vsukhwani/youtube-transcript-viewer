from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.transcript import handle_transcript_request
from api.languages import handle_languages_request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._send_cors_headers()
        self.end_headers()
    
    def _handle_request(self):
        try:
            # Parse the URL
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Set CORS headers
            self._send_cors_headers()
            
            if path.startswith('/api/transcript'):
                self._handle_transcript_api(query_params)
            elif path.startswith('/api/languages'):
                self._handle_languages_api(query_params)
            else:
                self._send_error(404, 'Not Found')
                
        except Exception as e:
            print(f"Error handling request: {e}")
            self._send_error(500, 'Internal Server Error')
    
    def _handle_transcript_api(self, query_params):
        try:
            # Get the request body if it's a POST request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Handle the transcript request
            response = handle_transcript_request(self, query_params, post_data)
            
            if response:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self._send_error(400, 'Bad Request')
                
        except Exception as e:
            print(f"Error in transcript API: {e}")
            self._send_error(500, str(e))
    
    def _handle_languages_api(self, query_params):
        try:
            # Get the request body if it's a POST request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Handle the languages request
            response = handle_languages_request(self, query_params, post_data)
            
            if response:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self._send_error(400, 'Bad Request')
                
        except Exception as e:
            print(f"Error in languages API: {e}")
            self._send_error(500, str(e))
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Origin, Referer')
    
    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
