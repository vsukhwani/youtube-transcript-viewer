from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
    YOUTUBE_API_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    YOUTUBE_API_AVAILABLE = False
    # Create dummy classes
    class YouTubeTranscriptApi:
        @staticmethod
        def get_transcript(*args, **kwargs):
            raise Exception("youtube-transcript-api not available in this environment")
    
    class TranscriptsDisabled(Exception):
        pass
    
    class NoTranscriptFound(Exception):
        pass
    
    class VideoUnavailable(Exception):
        pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def _handle_request(self):
        # Always set CORS headers first
        self._send_cors_headers()
        
        try:
            # Parse the URL
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Get POST data if available
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = {}
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
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                self._send_error(400, 'Invalid YouTube URL')
                return
            
            # Get transcript
            transcript_text = self._get_transcript(video_id, language)
            
            response = {
                'transcript': transcript_text,
                'video_id': video_id,
                'language': language or 'auto'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error in transcript API: {e}")
            self._send_error(500, str(e))
    
    
    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        return None
    
    def _get_transcript(self, video_id, language=None):
        """Get transcript for a video"""
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
            
            return '\n'.join(formatted_text)
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise Exception(f"No transcript available for this video: {str(e)}")
        except VideoUnavailable as e:
            raise Exception(f"Video is unavailable: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching transcript: {str(e)}")
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Origin, Referer')
    
    def _send_error(self, code, message):
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {'error': message, 'detail': message}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"Error sending error response: {e}")
            # Last resort - send minimal response
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Internal Server Error')
            except:
                pass
