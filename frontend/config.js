// Frontend Configuration for Static Website
window.CONFIG = {
    // Backend API URLs - automatically detects environment
    apiUrl: (() => {
        console.log('🔍 Detecting environment...');
        console.log('🔍 Protocol:', window.location.protocol);
        console.log('🔍 Hostname:', window.location.hostname);
        console.log('🔍 Full location:', window.location.href);
        
        // If accessing via file:// protocol (static website), use localhost backend
        if (window.location.protocol === 'file:') {
            console.log('🔍 Using local backend API for file:// protocol');
            return 'http://localhost:3002/api/transcript_v2';
        }
        // If running on localhost (development)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('🔍 Using local backend API for localhost');
            return 'http://localhost:3002/api/transcript_v2';
        }
        // If running on Vercel or other server, use main transcript endpoint
        console.log('🔍 Using relative API path for production');
        return '/api/transcript_v2';
    })(),
    helloApiUrl: (() => {
        // Use same logic as apiUrl for consistency
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/hello';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/hello';
        }
        return '/api/hello';
    })(),
    testApiUrl: (() => {
        // Add test API URL with same logic
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/test';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/test';
        }
        return '/api/test';
    })(),
    pingApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/ping';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/ping';
        }
        return '/api/ping';
    })(),
    indexApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api';
        }
        return '/api';
    })(),
    languagesApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/languages';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/languages';
        }
        return '/api/languages';
    })(),
    diagnosticApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/diagnostic';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/diagnostic';
        }
        return '/api/diagnostic';
    })(),
    networkTestApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/network_test';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/network_test';
        }
        return '/api/network_test';
    })(),
    transcriptTestApiUrl: (() => {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:3002/api/transcript_test';
        }
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3002/api/transcript_test';
        }
        return '/api/transcript_test';
    })(),
    
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
