// Frontend Configuration for Static Website
window.CONFIG = {
    // Backend API URLs - automatically detects environment
    apiUrl: (() => {
        // If accessing via file:// protocol (static website), use localhost backend
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/transcript_v2';
        }
        // If running on localhost (development)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/transcript_v2';
        }
        // If running on Vercel or other server, use relative paths
        return '/api/transcript_v2';
    })(),
    helloApiUrl: '/api/hello',
    
    // App settings
    defaultFontSize: 'medium',
    debug: true, // Always enable debug for troubleshooting
    apiKey: 'dev_api_key_1234567890',
    
    // Analytics disabled for now
    analytics: false
};

// Log configuration on load for debugging
console.log('Frontend Config Loaded:', {
    protocol: window.location.protocol,
    apiUrl: CONFIG.apiUrl,
    isStaticFile: window.location.protocol === 'file:'
});

// Dispatch config-loaded event
document.addEventListener('DOMContentLoaded', () => {
    const event = new CustomEvent('config-loaded');
    document.dispatchEvent(event);
});
