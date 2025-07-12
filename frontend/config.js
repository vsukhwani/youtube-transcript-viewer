// Frontend Configuration for Static Website
window.CONFIG = {
    // Backend API URLs - automatically detects environment
    apiUrl: (() => {
        // If accessing via file:// protocol (static website), use localhost backend
        if (window.location.protocol === 'file:') {
            return 'http://127.0.0.1:3002/api/transcript_v2';
        }
        // If running on localhost (development)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://127.0.0.1:3002/api/transcript_v2';
        }
        // If running on Vercel or other server, use relative paths
        return '/api/transcript_v2';
    })(),
    
    languagesApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://127.0.0.1:3002/api/languages_v4';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://127.0.0.1:3002/api/languages_v4';
        }
        return '/api/languages_v4';
    })(),
    
    // App settings
    defaultFontSize: 'medium',
    debug: window.location.hostname === 'localhost' || window.location.protocol === 'file:',
    
    // Analytics disabled for now
    analytics: false,
    
    // API key for backend authentication
    apiKey: (() => {
        // For production (Vercel), the API functions don't require API key validation
        // since they're serverless functions
        if (window.location.hostname.includes('vercel.app') || 
            (window.location.hostname !== 'localhost' && 
             window.location.hostname !== '127.0.0.1' && 
             window.location.protocol !== 'file:')) {
            return 'vercel-production-key';
        }
        // Use development API key for local development
        return 'dev_api_key_1234567890';
    })()
};

// Log configuration on load for debugging
console.log('Frontend Config Loaded:', {
    protocol: window.location.protocol,
    apiUrl: CONFIG.apiUrl,
    languagesApiUrl: CONFIG.languagesApiUrl,
    isStaticFile: window.location.protocol === 'file:'
});

// Dispatch config-loaded event
document.addEventListener('DOMContentLoaded', () => {
    const event = new CustomEvent('config-loaded');
    document.dispatchEvent(event);
});
