from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Transcript Diagnostic API - GET endpoint",
            "status": "success",
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                url = data.get('url', '')
            else:
                response = {'error': 'No data provided', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Extract video ID
            def extract_video_id(url):
                youtube_id_pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
                match = re.search(youtube_id_pattern, url)
                return match.group(1) if match else None
            
            video_id = extract_video_id(url)
            if not video_id:
                response = {'error': 'Invalid YouTube URL format', 'status': 'error'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Diagnostic information
            diagnostics = {
                'url': url,
                'video_id': video_id,
                'status': 'diagnostic'
            }
            
            # Try to import the library and get basic info
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                diagnostics['library_imported'] = True
                
                # Try to list available transcripts first
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    available_transcripts = []
                    
                    for transcript in transcript_list:
                        available_transcripts.append({
                            'language': transcript.language,
                            'language_code': transcript.language_code,
                            'is_generated': transcript.is_generated,
                            'is_translatable': transcript.is_translatable
                        })
                    
                    diagnostics['available_transcripts'] = available_transcripts
                    diagnostics['transcript_count'] = len(available_transcripts)
                    diagnostics['list_transcripts_success'] = True
                    
                    # If transcripts are available, try to fetch one
                    if available_transcripts:
                        try:
                            # Try the first available transcript
                            first_transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            diagnostics['first_transcript_success'] = True
                            diagnostics['first_transcript_entries'] = len(first_transcript)
                            diagnostics['first_transcript_sample'] = first_transcript[:2] if first_transcript else []
                        except Exception as transcript_error:
                            diagnostics['first_transcript_success'] = False
                            diagnostics['first_transcript_error'] = str(transcript_error)
                    else:
                        diagnostics['no_transcripts_reason'] = 'No transcripts found in list'
                    
                except Exception as list_error:
                    diagnostics['list_transcripts_success'] = False
                    diagnostics['list_transcripts_error'] = str(list_error)
                    diagnostics['list_transcripts_error_type'] = type(list_error).__name__
                    diagnostics['available_transcripts'] = []
                    
                    # Try direct get_transcript as fallback
                    try:
                        direct_transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        diagnostics['direct_transcript_success'] = True
                        diagnostics['direct_transcript_entries'] = len(direct_transcript)
                        diagnostics['direct_transcript_sample'] = direct_transcript[:2] if direct_transcript else []
                    except Exception as direct_error:
                        diagnostics['direct_transcript_success'] = False
                        diagnostics['direct_transcript_error'] = str(direct_error)
                        diagnostics['direct_transcript_error_type'] = type(direct_error).__name__
                    
            except ImportError as import_error:
                diagnostics['library_imported'] = False
                diagnostics['import_error'] = str(import_error)
            except Exception as general_error:
                diagnostics['library_imported'] = False
                diagnostics['general_error'] = str(general_error)
            
            self.wfile.write(json.dumps(diagnostics, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'error': f'Diagnostic error: {str(e)}',
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
