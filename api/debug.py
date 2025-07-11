from http.server import BaseHTTPRequestHandler
import json
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Try to import youtube_transcript_api
        try:
            import youtube_transcript_api
            import_status = "SUCCESS"
            version = getattr(youtube_transcript_api, '__version__', 'unknown')
            error_msg = None
        except ImportError as e:
            import_status = "FAILED"
            version = None
            error_msg = str(e)
        
        response = {
            'python_version': sys.version,
            'python_path': sys.path,
            'working_directory': os.getcwd(),
            'environment_vars': dict(os.environ),
            'youtube_transcript_api': {
                'import_status': import_status,
                'version': version,
                'error': error_msg
            }
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
