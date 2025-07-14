from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import ssl

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Network Diagnostic API - GET endpoint",
            "status": "success"
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
                video_id = data.get('video_id', 'dQw4w9WgXcQ')  # Default test video
            else:
                video_id = 'dQw4w9WgXcQ'
            
            diagnostics = {
                'video_id': video_id,
                'status': 'network_diagnostic'
            }
            
            # Test 1: Basic YouTube connectivity
            try:
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                req = urllib.request.Request(youtube_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    diagnostics['youtube_connectivity'] = {
                        'status': 'success',
                        'status_code': response.getcode(),
                        'headers': dict(response.headers)
                    }
            except Exception as e:
                diagnostics['youtube_connectivity'] = {
                    'status': 'failed',
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            
            # Test 2: Try different User-Agent strings
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'youtube-transcript-api/0.6.2',
                'python-requests/2.31.0',
                ''  # No user agent
            ]
            
            diagnostics['user_agent_tests'] = []
            
            for ua in user_agents:
                try:
                    req = urllib.request.Request(f"https://www.youtube.com/watch?v={video_id}")
                    if ua:
                        req.add_header('User-Agent', ua)
                    
                    with urllib.request.urlopen(req, timeout=5) as response:
                        diagnostics['user_agent_tests'].append({
                            'user_agent': ua or 'none',
                            'status': 'success',
                            'status_code': response.getcode()
                        })
                except Exception as e:
                    diagnostics['user_agent_tests'].append({
                        'user_agent': ua or 'none',
                        'status': 'failed',
                        'error': str(e),
                        'error_type': type(e).__name__
                    })
            
            # Test 3: Check if we can import and use the transcript library
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                
                diagnostics['library_info'] = {
                    'import_success': True,
                    'library_version': getattr(YouTubeTranscriptApi, '__version__', 'unknown')
                }
                
                # Test basic library functionality
                try:
                    # Test if we can actually use the library with a simple call
                    # We'll just check if the class methods are accessible
                    list_method = getattr(YouTubeTranscriptApi, 'list_transcripts', None)
                    get_method = getattr(YouTubeTranscriptApi, 'get_transcript', None)
                    
                    diagnostics['library_info']['methods_accessible'] = {
                        'list_transcripts': list_method is not None,
                        'get_transcript': get_method is not None
                    }
                except Exception as method_error:
                    diagnostics['library_info']['methods_accessible'] = False
                    diagnostics['library_info']['method_error'] = str(method_error)
                
            except ImportError as import_error:
                diagnostics['library_info'] = {
                    'import_success': False,
                    'import_error': str(import_error)
                }
            
            # Test 4: Environment information
            import os
            import platform
            
            diagnostics['environment'] = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'is_vercel': os.environ.get('VERCEL', 'false'),
                'vercel_env': os.environ.get('VERCEL_ENV', 'unknown'),
                'aws_region': os.environ.get('AWS_REGION', 'unknown'),
                'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'unknown')
            }
            
            # Test 5: SSL/TLS connectivity
            try:
                context = ssl.create_default_context()
                diagnostics['ssl_info'] = {
                    'ssl_version': ssl.OPENSSL_VERSION,
                    'check_hostname': context.check_hostname,
                    'verify_mode': str(context.verify_mode)
                }
            except Exception as ssl_error:
                diagnostics['ssl_info'] = {
                    'error': str(ssl_error)
                }
            
            self.wfile.write(json.dumps(diagnostics, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'error': f'Network diagnostic error: {str(e)}',
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
