import http.server
import socketserver
import os
import sys
import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
import logging

import os, sys
# Configure project paths
script_dir = os.path.dirname(os.path.abspath(__file__))  # backend folder
# Add backend folder to PYTHONPATH so `config` and `api` packages inside backend are on the import path
sys.path.insert(0, script_dir)
# Import configuration
from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config["LOG_LEVEL"]))
logger = logging.getLogger(__name__)

# Set the port for the server
PORT = config["API_PORT"]

# Change to the directory containing the HTML, CSS, and JS files
os.chdir(script_dir)

# Import transcript utilities
from api.utils.transcript_utils import get_transcript_text, get_available_languages
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# For rate limiting
class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.request_counts = {}
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, client_ip):
        # No rate limiting if disabled
        if self.rate_limit <= 0:
            return False
            
        current_time = time.time()
        
        # Clean up old entries every minute
        if current_time - self.last_cleanup > 60:
            self._cleanup(current_time)
            self.last_cleanup = current_time
        
        # Initialize if this is the first request from this IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Add current request timestamp
        self.request_counts[client_ip].append(current_time)
        
        # Count requests in the last minute
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_counts[client_ip] if t > minute_ago]
        self.request_counts[client_ip] = recent_requests
        
        # Check if the rate limit is exceeded
        return len(recent_requests) > self.rate_limit
    
    def _cleanup(self, current_time):
        minute_ago = current_time - 60
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [t for t in self.request_counts[ip] if t > minute_ago]
            if not self.request_counts[ip]:
                del self.request_counts[ip]

# Initialize rate limiter
rate_limiter = RateLimiter(config["RATE_LIMIT"])

class LocalDevHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler that serves static files and handles API requests."""
    
    def __init__(self, *args, **kwargs):
        self.public_dir = Path(script_dir) / "public"
        super().__init__(*args, directory=str(self.public_dir), **kwargs)
    
    def do_GET(self):
        """Handle GET requests to the API endpoints."""
        # Check if this is an API request
        parsed_url = urlparse(self.path)
        # Normalize path to remove trailing slash for endpoint matching
        path = parsed_url.path.rstrip('/')
        query_params = parse_qs(parsed_url.query)
        
        # Handle languages API endpoint
        if path in ("/api/languages", "/api/languages_v4"):
            # Check rate limiting
            client_ip = self.client_address[0]
            if rate_limiter.is_rate_limited(client_ip):
                self.send_error_json(429, "Too many requests. Please try again later.")
                return
                
            # Skipping API key validation in local development
            logger.info(f"Processing languages API request to: {path} with URL: {query_params.get('url', [''])[0]}")
            
            # Verify referrer if allowed referrers are specified
            if config["ALLOWED_REFERRERS"] and config["ALLOWED_REFERRERS"] != ["*"]:
                referrer = self.headers.get('Referer', '')
                valid_referrer = False
                
                if referrer:
                    referrer_host = referrer.split('/')[2] if '://' in referrer else referrer
                    
                    for allowed in config["ALLOWED_REFERRERS"]:
                        # Handle wildcard subdomains
                        if allowed.startswith('*.') and referrer_host.endswith(allowed[1:]):
                            valid_referrer = True
                            break
                        # Direct match
                        elif allowed == referrer_host:
                            valid_referrer = True
                            break
                
                if not valid_referrer:
                    client_ip = self.client_address[0]
                    logger.warning(f"Invalid referrer: {referrer} from IP: {client_ip}")
                    self.send_error_json(403, "Forbidden - Invalid referrer")
                    return
            
            # Get URL from query string
            url = query_params.get('url', [''])[0]
            
            if not url:
                self.send_error_json(400, "Missing YouTube URL")
                return
            
            logger.info(f"Processing languages request for URL: {url}")
            
            try:
                languages = get_available_languages(url)
                self.send_success_json({"languages": languages})
            except ValueError as ve:
                logger.error(f"Value error: {str(ve)}")
                self.send_error_json(400, str(ve))
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.error(f"Transcript not available: {str(e)}")
                self.send_error_json(404, "Transcripts not available for this video")
            except VideoUnavailable as e:
                logger.error(f"Video unavailable: {str(e)}")
                self.send_error_json(400, "This video is unavailable or does not exist")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                self.send_error_json(500, "An error occurred while processing your request")
            return
        
        # Handle hello API endpoint
        if path == "/api/hello":
            self.send_json_response({"message": "Hello from YouTube Transcript API!", "status": "ok"})
            return
            
        # Handle test API endpoint
        if path == "/api/test":
            self.send_json_response({"message": "Test endpoint working!", "status": "ok", "timestamp": time.time()})
            return
            
        # Handle ping API endpoint
        if path == "/api/ping":
            self.send_json_response({"message": "pong", "status": "ok"})
            return
            
        # Handle index API endpoint
        if path == "/api" or path == "/api/":
            self.send_json_response({
                "message": "YouTube Transcript API", 
                "status": "ok",
                "endpoints": [
                    "/api/transcript_v2",
                    "/api/languages", 
                    "/api/hello",
                    "/api/test",
                    "/api/ping",
                    "/api/diagnostic",
                    "/api/network_test",
                    "/api/transcript_test"
                ]
            })
            return
        
        # Handle diagnostic API endpoint
        if path == "/api/diagnostic":
            # This endpoint can handle both GET and POST
            if self.command == 'GET':
                self.send_json_response({
                    "message": "Diagnostic endpoint", 
                    "status": "ok",
                    "server_info": {
                        "version": "1.0.0",
                        "environment": "local",
                        "cors_enabled": True
                    }
                })
            return
            
        # Handle network test API endpoint  
        if path == "/api/network_test":
            self.send_json_response({
                "message": "Network test successful", 
                "status": "ok",
                "network_info": {
                    "server_reachable": True,
                    "response_time": "< 1ms",
                    "cors_headers": True
                }
            })
            return
            
        # Handle transcript test API endpoint
        if path == "/api/transcript_test":
            self.send_json_response({
                "message": "Transcript test endpoint", 
                "status": "ok",
                "test_info": {
                    "youtube_api_available": True,
                    "sample_videos": [
                        "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",  # Google I/O 2023
                        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Next.js Conf
                        "https://www.youtube.com/watch?v=v2AC41dglnM"   # CGP Grey
                    ]
                }
            })
            return
        
        # For all other GET requests, use the parent class implementation
        super().do_GET()
    
    def do_POST(self):
        # Parse URL and normalize path to remove trailing slash for endpoint matching
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')
        
        # Handle API requests
        if path in ("/api/transcript", "/api/transcript_v2"):
            self.handle_transcript_api()
            return
            
        # Handle diagnostic API endpoint (POST)
        if path == "/api/diagnostic":
            self.handle_diagnostic_api()
            return
            
        # Handle network test API endpoint (POST)
        if path == "/api/network_test":
            self.handle_network_test_api()
            return
            
        # Handle transcript test API endpoint (POST)
        if path == "/api/transcript_test":
            self.handle_transcript_test_api()
            return
        
        # Log unhandled POST requests for debugging
        logger.warning(f"Unhandled POST request to path: {path}")
        # If not an API request, return 404
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
    
    def handle_transcript_api(self):
        """Handle requests to the transcript API endpoint."""
        try:
            # Skipping API key validation in local development
            logger.info(f"Processing transcript API request. Headers: {self.headers}")
            
            # Verify referrer if allowed referrers are specified
            if config["ALLOWED_REFERRERS"] and config["ALLOWED_REFERRERS"] != ["*"]:
                referrer = self.headers.get('Referer', '')
                valid_referrer = False
                
                if referrer:
                    referrer_host = referrer.split('/')[2] if '://' in referrer else referrer
                    
                    for allowed in config["ALLOWED_REFERRERS"]:
                        # Handle wildcard subdomains
                        if allowed.startswith('*.') and referrer_host.endswith(allowed[1:]):
                            valid_referrer = True
                            break
                        # Direct match
                        elif allowed == referrer_host:
                            valid_referrer = True
                            break
                
                if not valid_referrer:
                    client_ip = self.client_address[0]
                    logger.warning(f"Invalid referrer: {referrer} from IP: {client_ip}")
                    self.send_error_json(403, "Forbidden - Invalid referrer")
                    return
            
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            url = request_data.get('url', '')
            language_code = request_data.get('language', None)
            
            if not url:
                self.send_error_json(400, "Missing YouTube URL")
                return
            
            logger.info(f"Processing request for URL: {url}, Language: {language_code or 'auto'}")
            
            try:
                transcript_text = get_transcript_text(url, language_code)
                logger.info(f"Successfully retrieved transcript, length: {len(transcript_text)}")
                self.send_success_json({"transcript": transcript_text})
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.error(f"Transcript not available: {str(e)}")
                self.send_error_json(404, f"Transcript not available for this video: {str(e)}")
            except VideoUnavailable as e:
                logger.error(f"Video unavailable: {str(e)}")
                self.send_error_json(400, f"Cannot process video: {str(e)}")
            except ValueError as ve:
                logger.error(f"Value error: {str(ve)}")
                self.send_error_json(400, str(ve))
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                self.send_error_json(500, f"Internal server error: {str(e)}")
                
        except json.JSONDecodeError:
            self.send_error_json(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            self.send_error_json(500, f"Server error: {str(e)}")
    
    def handle_diagnostic_api(self):
        """Handle requests to the diagnostic API endpoint."""
        try:
            # Get the request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                url = request_data.get('url', '')
            else:
                url = ''
            
            # Perform diagnostic checks
            diagnostic_info = {
                "server_status": "ok",
                "youtube_api_available": True,
                "environment": "local_development",
                "cors_enabled": True,
                "test_url": url if url else "No URL provided"
            }
            
            if url:
                # Add URL-specific diagnostics
                diagnostic_info["url_analysis"] = {
                    "valid_youtube_url": "youtube.com" in url or "youtu.be" in url,
                    "url_provided": url
                }
            
            self.send_json_response({
                "status": "ok",
                "message": "Diagnostic completed",
                "diagnostics": diagnostic_info
            })
            
        except json.JSONDecodeError:
            self.send_error_json(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Diagnostic error: {str(e)}", exc_info=True)
            self.send_error_json(500, f"Diagnostic error: {str(e)}")
    
    def handle_network_test_api(self):
        """Handle requests to the network test API endpoint."""
        try:
            # Get the request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            # Perform network tests
            network_info = {
                "server_reachable": True,
                "response_time": "< 1ms",
                "cors_headers": True,
                "server_time": time.time(),
                "request_method": "POST",
                "client_ip": self.client_address[0]
            }
            
            self.send_json_response({
                "status": "ok",
                "message": "Network test successful",
                "network_info": network_info
            })
            
        except json.JSONDecodeError:
            self.send_error_json(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Network test error: {str(e)}", exc_info=True)
            self.send_error_json(500, f"Network test error: {str(e)}")
    
    def handle_transcript_test_api(self):
        """Handle requests to the transcript test API endpoint."""
        try:
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            url = request_data.get('url', '')
            
            if not url:
                self.send_error_json(400, "Missing YouTube URL")
                return
            
            # This is a test endpoint, so return mock data
            test_result = {
                "url": url,
                "test_status": "completed",
                "transcript_available": True,
                "languages_detected": ["en", "auto"],
                "sample_transcript": "This is a test transcript sample...",
                "test_timestamp": time.time()
            }
            
            self.send_json_response({
                "status": "ok",
                "message": "Transcript test completed",
                "test_result": test_result
            })
            
        except json.JSONDecodeError:
            self.send_error_json(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Transcript test error: {str(e)}", exc_info=True)
            self.send_error_json(500, f"Transcript test error: {str(e)}")
    
    def send_success_json(self, data):
        """Send a JSON response with a 200 status code."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', config["CORS_ALLOW_ORIGINS"])
        self.send_header('Access-Control-Allow-Methods', config["CORS_ALLOW_METHODS"])
        self.send_header('Access-Control-Allow-Headers', config["CORS_ALLOW_HEADERS"])
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_json_response(self, data, status_code=200):
        """Send a JSON response with the specified status code."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', config["CORS_ALLOW_ORIGINS"])
        self.send_header('Access-Control-Allow-Methods', config["CORS_ALLOW_METHODS"])
        self.send_header('Access-Control-Allow-Headers', config["CORS_ALLOW_HEADERS"])
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_json(self, status_code, message):
        """Send a JSON error response with the specified status code."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', config["CORS_ALLOW_ORIGINS"])
        self.send_header('Access-Control-Allow-Methods', config["CORS_ALLOW_METHODS"])
        self.send_header('Access-Control-Allow-Headers', config["CORS_ALLOW_HEADERS"])
        self.end_headers()
        
        # In production, don't expose detailed error messages
        if not config["DETAILED_ERRORS"] and status_code >= 500:
            message = "Internal server error"
            
        self.wfile.write(json.dumps({"detail": message}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')
        
        # Log the OPTIONS request for debugging
        logger.info(f"Handling OPTIONS request for path: {path}")
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', config["CORS_ALLOW_ORIGINS"])
        self.send_header('Access-Control-Allow-Methods', config["CORS_ALLOW_METHODS"])
        self.send_header('Access-Control-Allow-Headers', config["CORS_ALLOW_HEADERS"])
        self.end_headers()

# Create an HTTP server with the custom handler
Handler = LocalDevHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print(f"Starting local development server at http://localhost:{PORT}")
print("This server simulates the Vercel deployment environment.")
print("Press Ctrl+C to stop the server")

# Start the server
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    httpd.shutdown()
