from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
import re

# Simple security configuration
REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'false').lower() == 'true'
VALID_API_KEYS = [
    os.environ.get('API_KEY', 'vercel-production-key'),  # For production
    'dev_api_key_1234567890',  # For development
    'vercel-production-key'    # Default for testing
]

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    youtube_id_pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(youtube_id_pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id, language=None):
    """Get transcript for a YouTube video"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # If language is specified, try that first
        if language and language != 'auto':
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            except Exception:
                # Fallback to default transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
        # Format transcript
        transcript_text = '\n'.join([f"[{int(entry['start'] // 60)}:{int(entry['start'] % 60):02d}] {entry['text']}" for entry in transcript])
        return transcript_text
    except Exception as e:
        raise e

class handler(BaseHTTPRequestHandler):
    def _validate_access(self):
        """Simple access validation"""
        if not REQUIRE_API_KEY:
            return True
        
        # Check for API key in headers
        api_key = self.headers.get('X-API-Key')
        if api_key and api_key in VALID_API_KEYS:
            return True
        
        # Check for API key in Authorization header
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token in VALID_API_KEYS:
                return True
        
        return False
    
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
        try:
            # Check access
            if not self._validate_access():
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized access", "status": "error"}).encode())
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            url = query_params.get('url', [''])[0]
            language = query_params.get('language', [None])[0]
            
            if not url:
                response = {'error': 'URL parameter is required', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Extract video ID
            video_id = extract_video_id(url)
            if not video_id:
                response = {'error': 'Invalid YouTube URL format', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return

            # Get transcript
            try:
                transcript = get_transcript(video_id, language)
                
                response = {
                    'transcript': transcript,
                    'video_id': video_id,
                    'language': language or 'auto',
                    'status': 'success'
                }
            except Exception as e:
                # Format error message
                error_str = str(e)
                error_lower = error_str.lower()
                
                status = "error"
                
                if "could not retrieve a transcript" in error_lower or "subtitles are disabled" in error_lower:
                    status = "no_transcripts"
                
                response = {
                    'error': error_str,
                    'video_id': video_id,
                    'status': status
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Last resort error handling
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                error_response = {'error': f'Server error: {str(e)}', 'status': 'error'}
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass
    
    def do_POST(self):
        try:
            # Check access
            if not self._validate_access():
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized access", "status": "error"}).encode())
                return
            
            # Parse POST data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                url = post_data.get('url', '')
                # Default to None so that default get_transcript is used when no explicit language
                language = post_data.get('language')
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                response = {'error': 'No data provided', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                response = {'error': 'URL parameter is required', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Extract video ID
            video_id = extract_video_id(url)
            if not video_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                response = {'error': 'Invalid YouTube URL format', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get transcript
            try:
                transcript = get_transcript(video_id, language)
                
                # Send successful response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                
                response = {
                    'transcript': transcript,
                    'video_id': video_id,
                    'language': language or 'auto',
                    'status': 'success'
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                # Format error message
                error_str = str(e)
                error_lower = error_str.lower()
                
                status_code = 200  # Always return 200 for API responses
                status = "error"
                
                if "could not retrieve a transcript" in error_lower or "subtitles are disabled" in error_lower:
                    status = "no_transcripts"
                
                # Send error response with 200 status
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                
                error_response = {
                    'error': error_str,
                    'video_id': video_id,
                    'status': status
                }
                self.wfile.write(json.dumps(error_response).encode())
                
        except Exception as e:
            # General error handling
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                
                error_response = {
                    'error': f'Server error: {str(e)}',
                    'status': 'error'
                }
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass
