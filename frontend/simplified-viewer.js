// Simplified version without language functionality
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 Loading simplified transcript viewer without language support');
    
    // Basic DOM elements
    const youtubeUrlInput = document.getElementById('youtube-url');
    const getTranscriptBtn = document.getElementById('get-transcript-btn');
    const transcriptContainer = document.getElementById('transcript-container');
    const transcriptContent = document.getElementById('transcript-content');
    const loadingIndicator = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const fontSizeSelect = document.getElementById('font-size');
    
    // Default font size
    const DEFAULT_FONT_SIZE = 'medium';
    
    // State variables
    let currentTranscript = '';
    let currentVideoId = '';
    
    // Initialize event listeners
    getTranscriptBtn.addEventListener('click', handleGetTranscript);
    youtubeUrlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleGetTranscript();
    });
    copyBtn.addEventListener('click', copyTranscriptToClipboard);
    downloadBtn.addEventListener('click', downloadTranscript);
    fontSizeSelect.addEventListener('change', (e) => {
        setFontSize(e.target.value);
        localStorage.setItem('transcriptFontSize', e.target.value);
    });
    
    // Set initial font size from preferences
    const savedFontSize = localStorage.getItem('transcriptFontSize') || DEFAULT_FONT_SIZE;
    setFontSize(savedFontSize);
    
    // Main transcript fetch function
    async function handleGetTranscript() {
        const url = youtubeUrlInput.value.trim();
        
        if (!url) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        if (!isValidYoutubeUrl(url)) {
            showError('Please enter a valid YouTube URL');
            return;
        }
        
        showLoading();
        
        // Save current video ID
        currentVideoId = extractVideoId(url);
        console.log('🔍 Processing video ID:', currentVideoId);
        
        try {
            console.log('🔍 About to fetch transcript...');
            const transcript = await fetchTranscript(url);
            console.log('🔍 Transcript fetched successfully, length:', transcript.length);
            displayTranscript(transcript);
        } catch (error) {
            console.error('Error fetching transcript:', error);
            let errorMessage = 'Failed to get transcript. Please try again.';
            
            try {
                if (error.detail) {
                    errorMessage = error.detail;
                } else if (error.message) {
                    errorMessage = error.message;
                }
            } catch (e) {
                console.error('Error parsing error message:', e);
            }
            
            showError(errorMessage);
        }
    }
    
    // Extract video ID from YouTube URL
    function extractVideoId(url) {
        const match = url.match(/(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
        return match ? match[1] : 'unknown';
    }
    
    // Validate YouTube URL
    function isValidYoutubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})([&?].*)?$/;
        return youtubeRegex.test(url);
    }
    
    // Fetch transcript from API
    async function fetchTranscript(url) {
        console.log('🔍 Using API endpoint:', CONFIG.apiUrl);
        console.log('🔍 API key present:', CONFIG.apiKey ? 'Yes' : 'No');
        
        try {
            const payload = { url };
            console.log('🔍 API request payload:', JSON.stringify(payload));
            
            // Create request options
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            };
            
            // Add API key if present
            if (CONFIG.apiKey) {
                options.headers['X-API-Key'] = CONFIG.apiKey;
                console.log('🔍 Added API key to request headers');
            }
            
            console.log('🔍 Sending fetch request to:', CONFIG.apiUrl);
            console.log('🔍 Request options:', JSON.stringify(options, (key, value) => 
                key === 'X-API-Key' ? '[HIDDEN]' : value));
            
            const response = await fetch(CONFIG.apiUrl, options);
            
            console.log('🔍 API response received, status:', response.status);
            
            if (!response.ok) {
                try {
                    const errorData = await response.json();
                    console.error('🔍 API error:', errorData);
                    throw errorData;
                } catch (jsonError) {
                    // If response is not JSON, handle it differently
                    const textData = await response.text();
                    console.error('🔍 API returned non-JSON response:', textData.substring(0, 200));
                    throw new Error(`API returned status ${response.status}: Non-JSON response`);
                }
            }
            
            try {
                const data = await response.json();
                console.log('🔍 Transcript API response data received');
                
                if (!data.transcript) {
                    throw new Error('No transcript found in response');
                }
                
                return data.transcript;
            } catch (jsonError) {
                console.error('🔍 JSON parsing error:', jsonError);
                throw new Error('Could not parse API response as JSON');
            }
        } catch (error) {
            console.error('🔍 Fetch error:', error);
            
            // Provide more helpful error messages for common issues
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                console.error('🔍 Network error detected. Backend API might not be responding.');
                
                // Different error messages based on environment
                if (window.location.protocol === 'file:' || 
                    window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1') {
                    throw {
                        detail: 'Cannot connect to backend server. Make sure the server is running at http://localhost:3002.'
                    };
                } else {
                    throw {
                        detail: 'Cannot connect to API. The server might be experiencing issues. Please try again later.'
                    };
                }
            } else if (error.message && error.message.includes('parse API response as JSON')) {
                // Special handling for HTML responses that were supposed to be JSON
                console.error('🔍 API returned HTML instead of JSON. This likely means the server-side routing is not working correctly.');
                throw {
                    detail: 'The API is returning HTML instead of JSON. Please visit /debug to troubleshoot.'
                };
            }
            
            throw error;
        }
    }
    
    // Display transcript
    function displayTranscript(transcript) {
        hideLoading();
        
        if (!transcript) {
            showError('No transcript found for this video');
            return;
        }
        
        // Save current transcript for copy/download
        currentTranscript = transcript;
        
        // Format transcript with paragraphs and timestamps
        const formattedTranscript = formatTranscript(transcript);
        transcriptContent.innerHTML = formattedTranscript;
        
        // Show transcript container
        errorMessage.classList.add('hidden');
        transcriptContainer.classList.remove('hidden');
        
        // Scroll to transcript
        transcriptContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Format transcript
    function formatTranscript(transcript) {
        const lines = transcript.split('\n');
        let formattedHtml = '';
        
        lines.forEach(line => {
            if (!line.trim()) return; // Skip empty lines
            
            // Check for timestamp format [MM:SS]
            const timestampMatch = line.match(/^\[(\d+:\d+)\]\s*(.*)/);
            
            if (timestampMatch) {
                const content = timestampMatch[2].trim();
                
                // Create HTML for this line
                let lineHtml = '<p>';
                
                // Check for speaker labels (e.g., "Speaker: Text")
                if (content.includes(':')) {
                    const parts = content.split(':');
                    // Only treat as speaker if the part before ":" is reasonably short
                    if (parts[0].length < 30) {
                        const speaker = parts.shift();
                        const text = parts.join(':').trim();
                        lineHtml += `<span class="speaker">${speaker}:</span> ${text}`;
                    } else {
                        lineHtml += content;
                    }
                } else {
                    lineHtml += content;
                }
                
                lineHtml += '</p>';
                formattedHtml += lineHtml;
            } else {
                // No timestamp found, just add the content
                formattedHtml += `<p>${line}</p>`;
            }
        });
        
        return formattedHtml;
    }
    
    // Copy transcript to clipboard
    async function copyTranscriptToClipboard() {
        if (!currentTranscript) return;
        
        try {
            await navigator.clipboard.writeText(currentTranscript);
            const copyNotification = document.getElementById('copy-notification');
            if (copyNotification) {
                copyNotification.classList.remove('hidden');
                setTimeout(() => {
                    copyNotification.classList.add('hidden');
                }, 2000);
            }
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    }
    
    // Download transcript as text file
    function downloadTranscript() {
        if (!currentTranscript) return;
        
        const filename = `transcript_${currentVideoId}.txt`;
        const blob = new Blob([currentTranscript], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    // Set font size
    function setFontSize(size) {
        if (!size || !['small', 'medium', 'large'].includes(size)) {
            size = DEFAULT_FONT_SIZE;
        }
        if (transcriptContent) {
            transcriptContent.className = `content-area font-${size}`;
        }
        if (fontSizeSelect) {
            fontSizeSelect.value = size;
        }
    }
    
    // UI helpers
    function showLoading() {
        loadingIndicator.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        transcriptContainer.classList.add('hidden');
    }
    
    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }
    
    function showError(message) {
        hideLoading();
        transcriptContainer.classList.add('hidden');
        errorMessage.classList.remove('hidden');
        errorText.textContent = message;
    }
    
    // Log success message
    console.log('🔍 Simplified transcript viewer initialized successfully');
});
