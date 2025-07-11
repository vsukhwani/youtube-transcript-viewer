from http.server import BaseHTTPRequestHandler
import json
import logging
import os
import sys
import time
import urllib.parse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config import config

# Import transcript utilities
from api.utils.transcript_utils import get_available_languages
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Configure logging
logging.basicConfig(level=getattr(logging, config["LOG_LEVEL"]))
logger = logging.getLogger(__name__)

# For rate limiting
rate_limits = {}
last_cleanup = time.time()

def is_rate_limited(client_ip):
    global last_cleanup, rate_limits
    
    # No rate limiting if disabled
    if config["RATE_LIMIT"] <= 0:
        return False
        
    current_time = time.time()
    
    # Clean up old entries every minute
    if current_time - last_cleanup > 60:
        cleanup_rate_limits(current_time)
        last_cleanup = current_time
    
    # Initialize if this is the first request from this IP
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []
    
    # Add current request timestamp
    rate_limits[client_ip].append(current_time)
    
    # Count requests in the last minute
    minute_ago = current_time - 60
    recent_requests = [t for t in rate_limits[client_ip] if t > minute_ago]
    rate_limits[client_ip] = recent_requests
    
    # Check if the rate limit is exceeded
    return len(recent_requests) > config["RATE_LIMIT"]

def cleanup_rate_limits(current_time):
    global rate_limits
    minute_ago = current_time - 60
    for ip in list(rate_limits.keys()):
        rate_limits[ip] = [t for t in rate_limits[ip] if t > minute_ago]
        if not rate_limits[ip]:
            del rate_limits[ip]

def cors_headers():
    return {
        "Access-Control-Allow-Origin": config["CORS_ALLOW_ORIGINS"],
        "Access-Control-Allow-Methods": config["CORS_ALLOW_METHODS"],
        "Access-Control-Allow-Headers": config["CORS_ALLOW_HEADERS"],
    }

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()

    def do_GET(self):
        # Check rate limiting
        client_ip = self.client_address[0]
        if is_rate_limited(client_ip):
            self._send_error(429, "Too many requests. Please try again later.")
            return
        
        # Verify API key if enabled
        if config["VERIFY_API_KEY"]:
            api_key = self.headers.get('X-API-Key')
            if not api_key or api_key != config["API_KEY"]:
                logger.warning(f"Invalid or missing API key from IP: {client_ip}")
                self._send_error(401, "Unauthorized - Invalid or missing API key")
                return
        
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
                logger.warning(f"Invalid referrer: {referrer} from IP: {client_ip}")
                self._send_error(403, "Forbidden - Invalid referrer")
                return
            
        # Parse query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        url = query_components.get('url', [''])[0]
        
        if not url:
            self._send_error(400, "Missing YouTube URL")
            return
        
        logger.info(f"Processing request for languages, URL: {url}")
        
        try:
            languages = get_available_languages(url)
            self._send_success({"languages": languages})
        except ValueError as ve:
            # This catches our custom error messages
            logger.error(f"Value error: {str(ve)}")
            self._send_error(400, str(ve))
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # This is a fallback for any transcript errors that weren't converted to ValueError
            logger.error(f"Transcript not available: {str(e)}")
            self._send_error(404, "Transcripts not available for this video")
        except VideoUnavailable as e:
            logger.error(f"Video unavailable: {str(e)}")
            self._send_error(400, "This video is unavailable or does not exist")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            self._send_error(500, "An error occurred while processing your request")

    def _send_success(self, data):
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status_code, message):
        self.send_response(status_code)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # In production, don't expose detailed error messages
        if not config["DETAILED_ERRORS"] and status_code >= 500:
            message = "Internal server error"
            
        self.wfile.write(json.dumps({"detail": message}).encode('utf-8'))
