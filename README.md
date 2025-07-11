# YouTube Transcript Viewer

A clean, modern web application for fetching and displaying YouTube video transcripts with multi-language support.

![YouTube Transcript Viewer](https://img.shields.io/badge/YouTube-Transcript%20Viewer-red?style=for-the-badge&logo=youtube)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=for-the-badge&logo=javascript)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

- 🎥 **YouTube Transcript Extraction** - Get transcripts from any YouTube video
- 🌍 **Multi-Language Support** - Access transcripts in all available languages
- 🎨 **Modern UI** - Clean, responsive design that works on all devices
- 📋 **Copy & Download** - Easy transcript copying and downloading
- 🔤 **Font Size Control** - Adjustable text size for better readability
- ⚡ **Fast & Lightweight** - No heavy frameworks, pure HTML/CSS/JavaScript
- 🔒 **Secure** - API key protection and CORS configuration

## 🏗️ Architecture

**Frontend**: Static website (HTML/CSS/JavaScript) that connects to a backend API
**Backend**: Python API server that fetches transcripts from YouTube using `youtube-transcript-api`

## 📁 Project Structure

```
transcript-app/
├── frontend/           # 🌐 Static Frontend
│   ├── index.html      # Main HTML file
│   ├── styles.css      # CSS styles
│   ├── script.js       # JavaScript application logic
│   ├── config.js       # Configuration
│   └── README.md       # Frontend documentation
├── backend/            # 🔧 Backend API server
│   ├── api/            # API endpoints
│   │   ├── transcript.py
│   │   ├── languages.py
│   │   └── utils/
│   ├── config/         # Environment configurations
│   │   ├── local.py
│   │   ├── production.py
│   │   └── __init__.py
│   ├── server.py       # Main backend server
│   ├── requirements.txt # Python dependencies
│   └── README.md       # Backend documentation
├── LAUNCH.bat          # Windows one-click launcher
├── setup.py            # Python setup script
├── start.py            # Alternative startup script
└── README.md           # This file
```

## 🚀 Quick Start

### Option 1: 🎯 **One-Click Launch (Windows)**
```bash
LAUNCH.bat    # Starts backend + opens frontend automatically
```

### Option 2: ⚙️ **Manual Setup**

#### 1. First-time Setup
```bash
python setup.py    # Creates virtual environment and installs dependencies
```

#### 2. Start Backend API
```bash
cd backend
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
python server.py
```

#### 3. Open Frontend (Choose one)
- **Easiest**: Double-click `frontend/index.html`
- **Alternative**: Drag `frontend/index.html` to your browser
- **Dev**: Run `start.py` from project root

### 🎯 **Using the Application**
1. Enter any YouTube URL
2. Click "Get Transcript" 
3. Select different languages if available
4. Copy or download the transcript

## 🌐 How It Works

The frontend automatically detects its environment:
- **File protocol** (`file://`): Connects to `http://127.0.0.1:3002`
- **Web server**: Uses relative paths for production deployment

No configuration needed - it just works!
4. Copy, download, or adjust font size as needed

## Features

- 🎥 **YouTube Transcript Extraction**: Enter any YouTube URL to get transcripts
- 🌍 **Multi-Language Support**: Automatically detects and allows switching between available languages
- 📝 **Clean Formatting**: Properly formatted transcripts with timestamps and speaker detection
- 📋 **Copy & Download**: Copy to clipboard or download transcripts as text files
- 🎨 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Fast & Lightweight**: Minimal dependencies, fast loading

## 🚀 Deployment

### Deploy to Vercel (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Connect your GitHub repository to Vercel
   - Set environment variables:
     - `API_KEY`: Your secure API key for production
     - `ENVIRONMENT`: `production`
   - Deploy with default settings

3. **Access your app**: Your app will be available at `https://your-app.vercel.app`

### Manual Deployment

The app can be deployed to any platform that supports:
- Static file hosting (frontend)
- Python serverless functions or containers (backend)

### Environment Variables

For production deployment, set these environment variables:
- `API_KEY`: Secure random string for API authentication
- `ENVIRONMENT`: Set to `production`

## 🛠️ Development

- **Frontend**: Static HTML/CSS/JavaScript - no build process needed!
- **Backend**: Python with minimal dependencies
- **API**: RESTful endpoints for transcript fetching
- **CORS**: Properly configured for cross-origin requests

## 📡 API Endpoints

- `POST /api/transcript` - Fetch transcript for a YouTube URL
- `POST /api/languages` - Get available languages for a YouTube video

**Request Format**:
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en" // optional
}
```

## ⚙️ Configuration

- Frontend config: `frontend/config.js` (auto-detects environment)
- Backend config: `backend/config/local.py` (local), `backend/config/production.py` (production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify as needed.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   YouTube API   │
│  (Static HTML)  │───▶│  (Python)       │───▶│   (Transcripts) │
│                 │    │                 │    │                 │
│ • JavaScript    │    │ • Serverless    │    │ • Multi-lang    │
│ • Auto-config   │    │ • CORS enabled  │    │ • Real-time     │
│ • Responsive    │    │ • Rate limited  │    │ • Reliable      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
