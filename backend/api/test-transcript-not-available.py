from http.server import BaseHTTPRequestHandler
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        This endpoint always returns a 404 error to simulate a video with no available transcript.
        """
        logger.info("Testing the 'transcript not available' error scenario")
        
        self.send_response(404)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        error_message = {
            "detail": "Transcript not available for this video: This is a test of the 'transcript not available' error."
        }
        
        self.wfile.write(json.dumps(error_message).encode('utf-8'))
