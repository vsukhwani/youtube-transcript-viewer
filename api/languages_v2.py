from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            url = query_params.get('url', [''])[0]
            
            if not url:
                response = {'error': 'URL parameter is required', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Try to import and use youtube_transcript_api
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                
                # Extract video ID
                if 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]
                elif 'youtube.com/watch?v=' in url:
                    video_id = url.split('v=')[1].split('&')[0]
                elif 'youtube.com/embed/' in url:
                    video_id = url.split('embed/')[1].split('?')[0]
                else:
                    response = {'error': 'Invalid YouTube URL format', 'status': 'error'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Get available languages
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                languages = []
                for transcript in transcript_list:
                    languages.append({
                        'language_code': transcript.language_code,
                        'language': transcript.language,
                        'is_generated': transcript.is_generated,
                        'is_translatable': transcript.is_translatable
                    })
                
                response = {
                    'languages': languages,
                    'video_id': video_id,
                    'status': 'success'
                }
                
            except Exception as e:
                # If listing fails, try to provide a default language option
                error_msg = str(e)
                if "Could not retrieve a transcript" in error_msg:
                    # Provide common language options as fallback
                    response = {
                        'languages': [
                            {'language_code': 'en', 'language': 'English', 'is_generated': True, 'is_translatable': False},
                            {'language_code': 'auto', 'language': 'Auto-detect', 'is_generated': True, 'is_translatable': False}
                        ],
                        'video_id': video_id,
                        'status': 'fallback',
                        'note': 'Could not list languages, providing common options. Try getting transcript directly.'
                    }
                else:
                    response = {
                        'error': f'Failed to get languages: {error_msg}',
                        'video_id': video_id if 'video_id' in locals() else 'unknown',
                        'status': 'error'
                    }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Last resort error handling
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': f'Server error: {str(e)}', 'status': 'error'}
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass
    
    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Parse POST data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                url = post_data.get('url', '')
            else:
                response = {'error': 'No data provided', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not url:
                response = {'error': 'URL parameter is required', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Try to import and use youtube_transcript_api
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                
                # Extract video ID
                if 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]
                elif 'youtube.com/watch?v=' in url:
                    video_id = url.split('v=')[1].split('&')[0]
                elif 'youtube.com/embed/' in url:
                    video_id = url.split('embed/')[1].split('?')[0]
                else:
                    response = {'error': 'Invalid YouTube URL format', 'status': 'error'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Get available languages
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                languages = []
                for transcript in transcript_list:
                    languages.append({
                        'language_code': transcript.language_code,
                        'language': transcript.language,
                        'is_generated': transcript.is_generated,
                        'is_translatable': transcript.is_translatable
                    })
                
                response = {
                    'languages': languages,
                    'video_id': video_id,
                    'status': 'success'
                }
                
            except Exception as e:
                # If listing fails, try to provide a default language option
                error_msg = str(e)
                if "Could not retrieve a transcript" in error_msg:
                    # Provide common language options as fallback
                    response = {
                        'languages': [
                            {'language_code': 'en', 'language': 'English', 'is_generated': True, 'is_translatable': False},
                            {'language_code': 'auto', 'language': 'Auto-detect', 'is_generated': True, 'is_translatable': False}
                        ],
                        'video_id': video_id,
                        'status': 'fallback',
                        'note': 'Could not list languages, providing common options. Try getting transcript directly.'
                    }
                else:
                    response = {
                        'error': f'Failed to get languages: {error_msg}',
                        'video_id': video_id if 'video_id' in locals() else 'unknown',
                        'status': 'error'
                    }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Last resort error handling
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': f'Server error: {str(e)}', 'status': 'error'}
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
