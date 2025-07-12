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
                else:
                    response = {'error': 'Invalid YouTube URL'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Get transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = '\n'.join([f"[{int(entry['start'])}s] {entry['text']}" for entry in transcript])
                
                response = {
                    'transcript': transcript_text,
                    'video_id': video_id,
                    'status': 'success'
                }
                
            except Exception as e:
                response = {
                    'error': f'Failed to get transcript: {str(e)}',
                    'video_id': video_id if 'video_id' in locals() else 'unknown'
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Last resort error handling
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': f'Server error: {str(e)}'}
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass
    
    def do_POST(self):
        self.do_GET()  # For now, handle POST the same as GET
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
