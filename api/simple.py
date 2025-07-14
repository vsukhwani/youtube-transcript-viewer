from http.server import BaseHTTPRequestHandler
import json
import os

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    import re
    youtube_id_pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(youtube_id_pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id, language=None):
    """Get transcript for a YouTube video"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # If language is specified, try that first
        if language:
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
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        """Handle POST requests to get transcript"""
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            # Parse request body
            if content_length > 0:
                request_body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(request_body)
                url = data.get('url', '')
                language = data.get('language')
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No request body provided", "status": "error"}).encode())
                return

            # Validate URL
            if not url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "URL is required", "status": "error"}).encode())
                return

            # Extract video ID
            video_id = extract_video_id(url)
            if not video_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid YouTube URL", "status": "error"}).encode())
                return

            # Get transcript
            try:
                transcript = get_transcript(video_id, language)
                
                # Send successful response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                
                response_data = {
                    "transcript": transcript,
                    "video_id": video_id,
                    "status": "success"
                }
                self.wfile.write(json.dumps(response_data).encode())
                
            except Exception as e:
                # Format error message
                error_str = str(e)
                error_lower = error_str.lower()
                
                status_code = 500
                status = "error"
                
                if "could not retrieve a transcript" in error_lower or "subtitles are disabled" in error_lower:
                    status_code = 404
                    status = "no_transcripts"
                
                # Send error response
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                
                error_response = {
                    "error": error_str,
                    "video_id": video_id,
                    "status": status
                }
                self.wfile.write(json.dumps(error_response).encode())
                
        except Exception as e:
            # General error handling
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            
            error_response = {
                "error": f"Server error: {str(e)}",
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response).encode())
