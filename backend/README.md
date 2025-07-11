# Backend - YouTube Transcript API

Python backend server providing API endpoints for YouTube transcript extraction.

## Features

- **RESTful API**: Clean API endpoints for transcript operations
- **Multi-Language Support**: Fetch transcripts in available languages
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Configured for cross-origin requests
- **Rate Limiting**: Built-in rate limiting for API protection

## API Endpoints

### POST /api/transcript
Fetch transcript for a YouTube video.

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "en" // optional, defaults to auto-detected
}
```

**Response:**
```json
{
    "transcript": "Full transcript text...",
    "language": "en",
    "video_id": "VIDEO_ID"
}
```

### POST /api/languages
Get available languages for a YouTube video.

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
    "languages": [
        {
            "code": "en",
            "name": "English",
            "type": "manual"
        },
        {
            "code": "es",
            "name": "Spanish",
            "type": "auto"
        }
    ]
}
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python server.py
```

Server runs on http://localhost:3002

## Configuration

Configuration files in `config/`:
- `local.py` - Local development settings
- `production.py` - Production settings

Environment is detected automatically or can be set via `ENVIRONMENT` variable.

## Dependencies

- `youtube-transcript-api` - Core transcript fetching
- Standard library only for HTTP server

## Error Codes

- `400` - Bad Request (invalid URL, missing parameters)
- `404` - Transcript not available
- `429` - Rate limit exceeded
- `500` - Internal server error

## Development

The server includes:
- CORS headers for development
- Request logging
- Error tracking
- Rate limiting
- Health check endpoint

## Deployment

For production:
1. Set `ENVIRONMENT=production`
2. Update `config/production.py` with production settings
3. Use a production WSGI server (gunicorn, uwsgi)
4. Configure reverse proxy (nginx) if needed
