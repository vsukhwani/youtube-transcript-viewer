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
    Get all available transcript languages for a YouTube video with enhanced error handling
    
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
        try:
            for transcript in transcript_list._manually_created_transcripts.values():
                languages.append({
                    "code": transcript.language_code,
                    "name": transcript.language,
                    "type": "manual"
                })
        except AttributeError:
            # Handle cases where the internal structure might be different
            logger.warning("Unable to access manually created transcripts via internal attribute")
            
        # Collect generated transcripts  
        try:
            for transcript in transcript_list._generated_transcripts.values():
                languages.append({
                    "code": transcript.language_code,
                    "name": transcript.language,
                    "type": "generated"
                })
        except AttributeError:
            # Handle cases where the internal structure might be different
            logger.warning("Unable to access generated transcripts via internal attribute")
        
        # Fallback: iterate through all transcripts if internal attributes failed
        if not languages:
            logger.info("Using fallback method to collect transcript languages")
            for transcript in transcript_list:
                languages.append({
                    "code": transcript.language_code,
                    "name": transcript.language,
                    "type": "auto-detected"
                })
            
        logger.info(f"Found {len(languages)} available transcript languages for video {video_id}")
        return languages
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"No transcripts available for video {video_id}: {str(e)}")
        raise ValueError(f"No transcripts available for this video. This may be due to: {str(e)}")
    except VideoUnavailable as e:
        logger.error(f"Video {video_id} is unavailable: {str(e)}")
        raise ValueError("This video is unavailable or does not exist")
    except Exception as e:
        logger.error(f"Unexpected error fetching languages for {video_id}: {str(e)}", exc_info=True)
        raise ValueError(f"Unable to fetch transcript languages. Error: {str(e)}")

def get_transcript_text(youtube_url, language_code=None):
    """
    Get transcript text for a YouTube video with multiple fallback strategies
    
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
    
    # Strategy 1: Try direct transcript fetch
    try:
        if language_code:
            # Get transcript in specified language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        else:
            # Auto-select transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
        logger.info(f"Successfully retrieved transcript via direct method, {len(transcript_list)} entries")
        return format_transcript(transcript_list)
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.warning(f"Direct transcript fetch failed for {video_id}: {str(e)}")
        # Continue to try alternative strategies
    except VideoUnavailable as e:
        logger.error(f"Video {video_id} is unavailable: {str(e)}")
        raise ValueError("This video is unavailable or does not exist")
    except Exception as e:
        logger.warning(f"Direct transcript fetch failed with unexpected error for {video_id}: {str(e)}")
        # Continue to try alternative strategies
    
    # Strategy 2: Try listing transcripts first, then fetch
    try:
        logger.info(f"Trying alternative approach: listing transcripts first for {video_id}")
        transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find the best transcript
        target_transcript = None
        
        if language_code:
            # Look for specific language
            try:
                target_transcript = transcript_list_obj.find_transcript([language_code])
            except NoTranscriptFound:
                logger.warning(f"Specific language {language_code} not found, trying auto-generated")
                # Fallback to auto-generated in that language
                try:
                    target_transcript = transcript_list_obj.find_generated_transcript([language_code])
                except NoTranscriptFound:
                    pass
        
        if not target_transcript:
            # Try English first, then auto-generated English, then any available
            try:
                target_transcript = transcript_list_obj.find_transcript(['en', 'en-US', 'en-GB'])
            except NoTranscriptFound:
                try:
                    target_transcript = transcript_list_obj.find_generated_transcript(['en', 'en-US', 'en-GB'])
                except NoTranscriptFound:
                    # Get any available transcript
                    all_transcripts = list(transcript_list_obj)
                    if all_transcripts:
                        target_transcript = all_transcripts[0]
        
        if target_transcript:
            transcript_data = target_transcript.fetch()
            logger.info(f"Successfully retrieved transcript via listing method, {len(transcript_data)} entries")
            return format_transcript(transcript_data)
        else:
            raise NoTranscriptFound("No transcripts found via listing method")
            
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"Alternative transcript fetch also failed for {video_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Alternative transcript fetch failed with unexpected error for {video_id}: {str(e)}", exc_info=True)
    
    # If all strategies failed, raise the final error
    if language_code:
        raise ValueError(f"Transcript not available in the selected language ({language_code}). The video may have transcripts disabled or may not be accessible from this server environment.")
    else:
        raise ValueError("Transcript not available for this video. The video may have transcripts disabled or may not be accessible from this server environment.")
