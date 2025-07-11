# YouTube Transcript Viewer

A modern web application that extracts and displays YouTube video transcripts with multi-language support. Built with Python backend and vanilla JavaScript frontend, optimized for Vercel deployment.

## ✨ Features

- 🎯 **Extract transcripts** from any YouTube video
- 🌍 **Multi-language support** with automatic language detection
- 🔄 **Language switching** with persistent selection
- 📋 **Copy to clipboard** functionality
- 📥 **Download transcripts** as text files
- 🎨 **Responsive design** that works on all devices
- ⚡ **Fast and lightweight** - no heavy frameworks
- 🚀 **Serverless deployment** ready for Vercel

## 🚀 Live Demo

Deploy your own instance:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/transcript-app)

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** with built-in HTTP server
- **youtube-transcript-api** for transcript extraction
- **Serverless functions** compatible with Vercel
- **CORS enabled** for frontend integration

### Frontend
- **Vanilla JavaScript** (no frameworks!)
- **Modern CSS** with responsive design
- **Font Awesome** icons
- **Static files** served efficiently

## 📦 Installation & Local Development

### Prerequisites
- Python 3.11 or higher
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/transcript-app.git
   cd transcript-app
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python start.py
   ```
   
   Or use the Windows batch file:
   ```cmd
   LAUNCH.bat
   ```

4. **Open the frontend**
   - Navigate to `frontend/index.html` in your browser
   - Or use: `file:///path/to/transcript-app/frontend/index.html`

The backend will run on `http://localhost:3002` and the frontend will connect to it automatically.

## 🌐 Deployment to Vercel

This app is optimized for Vercel deployment with serverless functions.

### Automatic Deployment

1. **Fork this repository** on GitHub
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the configuration

3. **Deploy**:
   - Vercel will automatically build and deploy
   - Your app will be available at `https://your-app.vercel.app`

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 📁 Project Structure

```
transcript-app/
├── api/                    # Vercel serverless functions
│   ├── index.py           # Main API endpoint
│   ├── languages.py       # Language detection endpoint
│   └── transcript.py      # Transcript extraction endpoint
├── backend/               # Local development backend
│   ├── api/               # API modules
│   ├── config/            # Configuration files
│   └── server.py          # Local development server
├── frontend/              # Static frontend files
│   ├── index.html         # Main HTML file
│   ├── script.js          # JavaScript functionality
│   ├── styles.css         # CSS styling
│   └── config.js          # API configuration
├── vercel.json            # Vercel deployment config
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

For production deployment, you can set these environment variables in Vercel:

- `API_KEY`: API key for authentication (optional)
- `DEBUG`: Set to `false` for production
- `CORS_ALLOW_ORIGINS`: Allowed origins for CORS

### Local Development

Configuration is handled in `backend/config/local.py`:

- **Port**: 3002 (default)
- **CORS**: Enabled for all origins
- **Debug**: Enabled
- **Rate limiting**: Disabled

## 🎯 Usage

1. **Enter a YouTube URL** in the input field
2. **Click "Get Transcript"** to extract the transcript
3. **Select a language** if multiple are available
4. **Use the controls** to:
   - Copy transcript to clipboard
   - Download as text file
   - Change font size
   - Switch languages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Issues & Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/transcript-app/issues) page
2. Create a new issue with detailed information
3. Include browser console logs if applicable

## 🙏 Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
- [Font Awesome](https://fontawesome.com/) for icons
- [Vercel](https://vercel.com/) for hosting platform

---

Made with ❤️ by [Vikas Sukhwani](https://github.com/yourusername)
