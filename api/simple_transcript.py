from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
    IMPORT_SUCCESS = True
    IMPORT_ERROR = None
except ImportError as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Origin, Referer')
        self.end_headers()
    
    def _handle_request(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Origin, Referer')
        
        if not IMPORT_SUCCESS:
            self._send_error(500, f"Import failed: {IMPORT_ERROR}")
            return
        
        try:
            # Parse URL parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Get POST data if available
            post_data = {}
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                try:
                    post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_error(400, 'Invalid JSON in request body')
                    return
            
            # Extract parameters
            url = post_data.get('url') or (query_params.get('url', [''])[0])
            language = post_data.get('language') or (query_params.get('language', [''])[0])
            
            if not url:
                self._send_error(400, 'URL parameter is required')
                return
            
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                self._send_error(400, 'Invalid YouTube URL')
                return
            
            # Get transcript
            try:
                if language:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
                else:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                
                # Format transcript
                formatted_text = []
                for entry in transcript:
                    start_time = int(entry['start'])
                    minutes = start_time // 60
                    seconds = start_time % 60
                    timestamp = f"[{minutes}:{seconds:02d}]"
                    formatted_text.append(f"{timestamp} {entry['text']}")
                
                transcript_text = '\n'.join(formatted_text)
                
                response = {
                    'transcript': transcript_text,
                    'video_id': video_id,
                    'language': language or 'auto'
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                self._send_error(404, f"No transcript available for this video: {str(e)}")
            except VideoUnavailable as e:
                self._send_error(404, f"Video is unavailable: {str(e)}")
            except Exception as e:
                self._send_error(500, f"Error fetching transcript: {str(e)}")
            
        except Exception as e:
            self._send_error(500, f"Server error: {str(e)}")
    
    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        return None
    
    def _send_error(self, code, message):
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {'error': message, 'detail': message}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"Error sending error response: {e}")
