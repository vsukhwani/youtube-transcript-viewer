# Frontend - YouTube Transcript Viewer

**Static webpage** for the YouTube Transcript Viewer application. No server required!

## Features

- **🌐 Static Website**: Runs directly in the browser without any server
- **🎨 Clean Interface**: Intuitive design with modern UI elements
- **🌍 Language Selection**: Dropdown to select from available transcript languages
- **⚡ Real-time Updates**: Dynamic loading states and error handling
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **♿ Accessibility**: Keyboard navigation and screen reader friendly
- **🔤 Font Controls**: Adjustable font sizes for better readability

## Files

- `index.html` - Main HTML structure (open this in your browser!)
- `styles.css` - CSS styles with CSS variables for theming
- `script.js` - JavaScript application logic
- `config.js` - Configuration file that auto-detects environment

## 🚀 How to Use

### Option 1: Direct File Access (Simplest)
1. Make sure the backend is running on `http://localhost:3002`
2. Simply **double-click** `index.html` or drag it to your browser
3. That's it! The app will automatically connect to your local backend

### Option 2: Via Web Server (Optional)
If you prefer serving through a web server:
1. Use any static web server (Python, Node.js, Apache, Nginx, etc.)
2. Point it to this directory
3. Update `config.js` if needed for different backend URLs

## Configuration

The `config.js` file automatically detects the environment:

```javascript
// Automatically uses localhost:3002 when opened as file://
// Uses relative paths when served from a web server
```

For custom backend URLs, edit the config file directly.

## 🌐 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 📦 Deployment

For production deployment:

1. **Static Hosting**: Upload to any static hosting service:
   - GitHub Pages
   - Netlify
   - Vercel
   - AWS S3
   - Any web server

2. **Backend Setup**: Deploy the backend API and update `config.js` with production URLs

3. **CORS**: Ensure your backend allows requests from your domain

## 🔧 No Dependencies Required

- ✅ Pure HTML, CSS, and vanilla JavaScript
- ✅ Font Awesome (loaded from CDN)
- ✅ No build process needed
- ✅ No package.json or npm required
- ✅ Works offline (after initial load)
