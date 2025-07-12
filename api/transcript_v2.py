from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os

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
                response = {'error': 'URL parameter is required'}
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
                    response = {'error': 'Invalid YouTube URL format'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Get transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = '\n'.join([f"[{int(entry['start'])}s] {entry['text']}" for entry in transcript])
                
                response = {
                    'transcript': transcript_text,
                    'video_id': video_id,
                    'language': 'auto',
                    'status': 'success'
                }
                
            except Exception as e:
                response = {
                    'error': f'Failed to get transcript: {str(e)}',
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
                language = post_data.get('language', 'en')
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
                
                # Get transcript with language if specified
                if language and language != 'auto':
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
                else:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                
                transcript_text = '\n'.join([f"[{int(entry['start'])}s] {entry['text']}" for entry in transcript])
                
                response = {
                    'transcript': transcript_text,
                    'video_id': video_id,
                    'language': language,
                    'status': 'success'
                }
                
            except Exception as e:
                response = {
                    'error': f'Failed to get transcript: {str(e)}',
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
