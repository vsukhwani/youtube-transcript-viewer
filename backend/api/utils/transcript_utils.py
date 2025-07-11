import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound,
    VideoUnavailable
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_video_id(url):
    # Check if it's a YouTube Short
    if "/shorts/" in url:
        match = re.search(r"\/shorts\/([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None
    # Regular YouTube video
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def format_transcript(transcript_list):
    formatted_lines = []
    for item in transcript_list:
        # Format time in minutes:seconds
        time_in_seconds = item['start']
        minutes = int(time_in_seconds // 60)
        seconds = int(time_in_seconds % 60)
        timestamp = f"[{minutes}:{seconds:02d}]"
        
        # Add timestamp to text
        formatted_lines.append(f"{timestamp} {item['text']}")
    
    return '\n'.join(formatted_lines)

def get_available_languages(youtube_url):
    """
    Get all available transcript languages for a YouTube video
    
    Args:
        youtube_url (str): YouTube video URL or ID
        
    Returns:
        list: List of dictionaries with language details (code, name)
        
    Raises:
        ValueError: If URL is invalid or no transcripts are available
    """
    video_id = get_video_id(youtube_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    logger.info(f"Fetching available languages for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = []
        
        # Collect manual transcripts
        for transcript in transcript_list._manually_created_transcripts.values():
            languages.append({
                "code": transcript.language_code,
                "name": transcript.language,
                "type": "manual"
            })
            
        # Collect generated transcripts
        for transcript in transcript_list._generated_transcripts.values():
            languages.append({
                "code": transcript.language_code,
                "name": transcript.language,
                "type": "generated"
            })
            
        return languages
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"No transcripts available for video {video_id}: {str(e)}")
        raise ValueError("No transcripts available for this video")
    except VideoUnavailable as e:
        logger.error(f"Video {video_id} is unavailable: {str(e)}")
        raise ValueError("This video is unavailable or does not exist")
    except Exception as e:
        logger.error(f"Unexpected error fetching languages for {video_id}: {str(e)}", exc_info=True)
        raise

def get_transcript_text(youtube_url, language_code=None):
    """
    Get transcript text for a YouTube video
    
    Args:
        youtube_url (str): YouTube video URL or ID
        language_code (str, optional): Language code for transcript. Defaults to None (auto-select).
        
    Returns:
        str: Formatted transcript text
        
    Raises:
        ValueError: If URL is invalid or transcript is not available
    """
    video_id = get_video_id(youtube_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    logger.info(f"Attempting to fetch transcript for video ID: {video_id}, language: {language_code or 'auto'}")
    try:
        if language_code:
            # Get transcript in specified language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        else:
            # Auto-select transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
        return format_transcript(transcript_list)
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        # Log the detailed error for debugging
        logger.error(f"No transcript available for video {video_id}: {str(e)}")
        # Instead of re-raising the same exception, raise a ValueError with a user-friendly message
        if language_code:
            raise ValueError(f"Transcript not available in the selected language ({language_code})")
        else:
            raise ValueError("Transcript not available for this video")
    except VideoUnavailable as e:
        logger.error(f"Video {video_id} is unavailable: {str(e)}")
        raise ValueError("This video is unavailable or does not exist")
    except Exception as e:
        logger.error(f"Unexpected error fetching transcript for {video_id}: {str(e)}", exc_info=True)
        raise
