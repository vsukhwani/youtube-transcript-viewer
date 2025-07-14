// Function to hide language UI elements
function hideLanguageUI() {
    // Hide language selection UI elements
    if (languageSelection) {
        languageSelection.style.display = 'none';
    } else {
        console.log('🔍 languageSelection element not found');
    }
    
    if (transcriptLanguageSelection) {
        transcriptLanguageSelection.style.display = 'none';
    } else {
        console.log('🔍 transcriptLanguageSelection element not found');
    }
    
    // Hide any other language-related elements
    const languageElements = document.querySelectorAll('.language-selection-container, .language-selection');
    languageElements.forEach(el => {
        el.style.display = 'none';
    });
    console.log('🔍 All language UI elements hidden');
}

// Function to hide language selection
function hideLanguageSelection() {
    if (languageSelection) {
        languageSelection.classList.add('hidden');
    }
    
    if (transcriptLanguageSelection) {
        transcriptLanguageSelection.innerHTML = '';
    }
}

// Modified fetchTranscript to not use language parameter
async function fetchTranscript(url) {
    const apiUrl = CONFIG.apiUrl;
    
    if (CONFIG.debug) {
        console.log('Current CONFIG state:', {
            apiUrl: CONFIG.apiUrl,
            apiKey: CONFIG.apiKey ? 'Set (not showing for security)' : 'NOT SET',
            debug: CONFIG.debug
        });
        console.log('Fetching transcript for URL:', url);
        console.log('Using API endpoint:', apiUrl);
    }
    
    // Ensure API key is set
    if (!CONFIG.apiKey) {
        console.error('API key is not set! Check CONFIG initialization.');
        throw new Error('Configuration error: API key is not set');
    }
    
    try {
        const payload = { url };
        
        // Log the full payload for debugging
        console.log('🔍 API request payload:', JSON.stringify(payload));
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
        });
        
        if (CONFIG.debug) {
            console.log('API response status:', response.status);
        }
        
        // Handle rate limiting
        if (response.status === 429) {
            throw new Error('Too many requests. Please try again later.');
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            if (CONFIG.debug) {
                console.error('API error:', errorData);
            }
            // Throw the error object directly so we can access its properties
            throw errorData;
        }
        
        const data = await response.json();
        if (CONFIG.debug) {
            console.log('Transcript API response data:', data);
        }
        
        // Handle different API statuses
        if (data.status === 'no_transcripts') {
            // Surface the no transcripts error to UI
            throw data;
        }
        if (data.status !== 'success') {
            // Any other error status
            throw data;
        }
        
        return data.transcript;
    } catch (error) {
        if (CONFIG.debug) {
            console.error('Fetch error:', error);
        }
        throw error;
    }
}
