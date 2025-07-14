from http.server import BaseHTTPRequestHandler
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Test with videos that are known to have transcripts
        test_videos = [
            {
                "title": "Google I/O 2024 Keynote",
                "url": "https://www.youtube.com/watch?v=ddcZnW1HKUY",
                "video_id": "ddcZnW1HKUY",
                "reason": "Official Google video, likely has captions"
            },
            {
                "title": "TED: How to speak so that people want to listen",
                "url": "https://www.youtube.com/watch?v=eIho2S0ZahI", 
                "video_id": "eIho2S0ZahI",
                "reason": "Popular TED talk with millions of views"
            },
            {
                "title": "Minecraft Official Trailer",
                "url": "https://www.youtube.com/watch?v=MmB9b5njVbA",
                "video_id": "MmB9b5njVbA", 
                "reason": "Gaming video, often has auto-generated captions"
            },
            {
                "title": "NASA Mars Landing",
                "url": "https://www.youtube.com/watch?v=4czjS9h4Fpg",
                "video_id": "4czjS9h4Fpg",
                "reason": "Educational content, likely has captions"
            }
        ]
        
        response = {
            "message": "Test transcript endpoint with known working videos",
            "test_videos": test_videos,
            "instructions": "POST to this endpoint with 'auto_test': true to run tests"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
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
            else:
                data = {}
            
            if data.get('auto_test', False):
                # Run automatic tests with known videos
                results = self.run_transcript_tests()
            else:
                # Test specific video
                url = data.get('url', '')
                if not url:
                    self.wfile.write(json.dumps({"error": "URL required"}).encode())
                    return
                results = self.test_single_video(url)
            
            self.wfile.write(json.dumps(results, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'error': f'Test error: {str(e)}',
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def run_transcript_tests(self):
        """Test multiple known videos that should have transcripts"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        except ImportError as e:
            return {"error": f"Import failed: {str(e)}", "library_available": False}
        
        test_videos = [
            {"id": "ddcZnW1HKUY", "title": "Google I/O 2024 Keynote"},
            {"id": "eIho2S0ZahI", "title": "TED: How to speak so that people want to listen"},
            {"id": "MmB9b5njVbA", "title": "Minecraft Official Trailer"},
            {"id": "4czjS9h4Fpg", "title": "NASA Mars Landing"},
            {"id": "dQw4w9WgXcQ", "title": "Never Gonna Give You Up (Rick Roll)"},
            {"id": "jNQXAC9IVRw", "title": "Me at the zoo (First YouTube video)"}
        ]
        
        results = {
            "library_available": True,
            "test_results": [],
            "summary": {"total": len(test_videos), "successful": 0, "failed": 0}
        }
        
        for video in test_videos:
            video_id = video["id"]
            title = video["title"]
            
            test_result = {
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            
            try:
                # Try to list transcripts first
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                available_languages = []
                
                for transcript in transcript_list:
                    available_languages.append({
                        "code": transcript.language_code,
                        "name": transcript.language,
                        "is_generated": transcript.is_generated
                    })
                
                test_result["transcript_list_success"] = True
                test_result["available_languages"] = available_languages
                test_result["language_count"] = len(available_languages)
                
                # Try to fetch the first available transcript
                if available_languages:
                    try:
                        first_lang = available_languages[0]["code"]
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[first_lang])
                        test_result["transcript_fetch_success"] = True
                        test_result["transcript_entries"] = len(transcript_data)
                        test_result["sample_text"] = transcript_data[0]["text"] if transcript_data else ""
                        results["summary"]["successful"] += 1
                    except Exception as fetch_error:
                        test_result["transcript_fetch_success"] = False
                        test_result["fetch_error"] = str(fetch_error)
                        results["summary"]["failed"] += 1
                else:
                    test_result["transcript_fetch_success"] = False
                    test_result["fetch_error"] = "No languages available"
                    results["summary"]["failed"] += 1
                    
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                test_result["transcript_list_success"] = False
                test_result["list_error"] = str(e)
                test_result["error_type"] = "transcripts_disabled_or_not_found"
                results["summary"]["failed"] += 1
            except VideoUnavailable as e:
                test_result["transcript_list_success"] = False
                test_result["list_error"] = str(e)
                test_result["error_type"] = "video_unavailable"
                results["summary"]["failed"] += 1
            except Exception as e:
                test_result["transcript_list_success"] = False
                test_result["list_error"] = str(e)
                test_result["error_type"] = "unexpected_error"
                results["summary"]["failed"] += 1
            
            results["test_results"].append(test_result)
        
        return results
    
    def test_single_video(self, url):
        """Test a single video URL"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import re
        except ImportError as e:
            return {"error": f"Import failed: {str(e)}", "library_available": False}
        
        # Extract video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        if not video_id_match:
            return {"error": "Invalid YouTube URL", "url": url}
        
        video_id = video_id_match.group(1)
        
        result = {
            "url": url,
            "video_id": video_id,
            "library_available": True
        }
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            result["transcript_list_success"] = True
            
            available_languages = []
            for transcript in transcript_list:
                available_languages.append({
                    "code": transcript.language_code,
                    "name": transcript.language,
                    "is_generated": transcript.is_generated
                })
            
            result["available_languages"] = available_languages
            result["language_count"] = len(available_languages)
            
        except Exception as e:
            result["transcript_list_success"] = False
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
        
        return result
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
