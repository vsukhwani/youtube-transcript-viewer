from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
except ImportError:
    # Fallback if the package is not available
    class YouTubeTranscriptApi:
        @staticmethod
        def list_transcripts(*args, **kwargs):
            raise Exception("youtube-transcript-api not available")

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
            
            if not url:
                self._send_error(400, 'URL parameter is required')
                return
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                self._send_error(400, 'Invalid YouTube URL')
                return
            
            # Get available languages
            languages = self._get_available_languages(video_id)
            
            response = {
                'video_id': video_id,
                'languages': languages
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error in languages API: {e}")
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
    
    def _get_available_languages(self, video_id):
        """Get available languages for a video"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            languages = []
            for transcript in transcript_list:
                lang_info = {
                    'code': transcript.language_code,
                    'name': transcript.language,
                    'type': 'manual' if transcript.is_generated else 'auto'
                }
                languages.append(lang_info)
            
            return languages
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise Exception(f"No transcripts available for this video: {str(e)}")
        except VideoUnavailable as e:
            raise Exception(f"Video is unavailable: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching available languages: {str(e)}")
    
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
