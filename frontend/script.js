// DOM Elements
const youtubeUrlInput = document.getElementById('youtube-url');
const getTranscriptBtn = document.getElementById('get-transcript-btn');
const transcriptContainer = document.getElementById('transcript-container');
const transcriptContent = document.getElementById('transcript-content');
const loadingIndicator = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const copyNotification = document.getElementById('copy-notification');
const fontSizeSelect = document.getElementById('font-size');
const languageSelection = document.getElementById('language-selection');
const transcriptLanguageSelection = document.getElementById('transcript-language-selection');
const languageSelect = document.getElementById('language-select');
const changeLanguageBtn = document.getElementById('change-language-btn');

// Make sure CONFIG has been initialized
if (typeof CONFIG === 'undefined') {
    console.warn('CONFIG not found, initializing with defaults');
    window.CONFIG = {
        apiUrl: 'http://127.0.0.1:3002/api/transcript',
        languagesApiUrl: 'http://127.0.0.1:3002/api/languages',
        apiKey: 'dev_api_key_1234567890',
        defaultFontSize: 'medium',
        debug: true
    };
}

// Default font size from CONFIG
const DEFAULT_FONT_SIZE = CONFIG.defaultFontSize || 'medium';

// State variables
let currentTranscript = '';
let currentVideoId = '';
let availableLanguages = [];
let currentLanguage = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 Static frontend initialized');
    console.log('🔍 API URL:', CONFIG.apiUrl);
    console.log('🔍 Languages API URL:', CONFIG.languagesApiUrl);
    console.log('🔍 Running as static file:', window.location.protocol === 'file:');

    // Check if CONFIG is ready or wait for the config-loaded event
    if (typeof CONFIG !== 'undefined' && CONFIG.apiKey) {
        initEventListeners();
        setFontSize(getFontSizePreference());
    } else {
        // Wait for the config to be loaded
        document.addEventListener('config-loaded', () => {
            console.log('CONFIG loaded, initializing app');
            initEventListeners();
            setFontSize(getFontSizePreference());
        });
    }
});

// Event Listeners
function initEventListeners() {
    getTranscriptBtn.addEventListener('click', handleGetTranscript);
    youtubeUrlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleGetTranscript();
    });
    copyBtn.addEventListener('click', copyTranscriptToClipboard);
    downloadBtn.addEventListener('click', downloadTranscript);
    fontSizeSelect.addEventListener('change', (e) => {
        setFontSize(e.target.value);
        saveFontSizePreference(e.target.value);
    });
    
    if (languageSelect) {
        languageSelect.addEventListener('change', handleLanguageChange);
    }
    
    if (changeLanguageBtn) {
        changeLanguageBtn.addEventListener('click', () => {
            if (currentVideoId && languageSelect.value) {
                fetchTranscriptWithLanguage(youtubeUrlInput.value, languageSelect.value);
            }
        });
    }
}

// Get and display transcript
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
    resetLanguageSelection();
    
    // Save current video ID
    currentVideoId = extractVideoId(url);
    console.log('🔍 Processing video ID:', currentVideoId);
    
    try {
        // Skip backend health check for now since endpoint doesn't exist
        // Instead, we'll let the API calls fail gracefully
        
        // Fetch available languages first
        console.log('🔍 Fetching available languages');
        const languages = await fetchAvailableLanguages(url);
        availableLanguages = languages || [];
        console.log('🔍 Found languages:', availableLanguages.length);
        
        // Sort languages to prioritize manual transcripts
        if (availableLanguages.length > 0) {
            availableLanguages.sort((a, b) => {
                if (a.type === 'manual' && b.type !== 'manual') return -1;
                if (a.type !== 'manual' && b.type === 'manual') return 1;
                return a.name.localeCompare(b.name);
            });
        }
        
        // Set current language to first available language or null
        currentLanguage = availableLanguages.length > 0 ? availableLanguages[0].code : null;
        
        // Fetch transcript
        console.log('🔍 About to fetch transcript...');
        const transcript = await fetchTranscript(url, currentLanguage);
        console.log('🔍 Transcript fetched successfully, length:', transcript.length);
        console.log('🔍 About to display transcript...');
        displayTranscript(transcript);
        console.log('🔍 Transcript displayed successfully');
        
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

// Check if backend server is available
async function checkBackendHealth() {
    try {
        const healthUrl = CONFIG.apiUrl.replace('/api/transcript', '/health');
        const response = await fetch(healthUrl, { 
            method: 'GET',
            timeout: 5000 
        });
        return response.ok;
    } catch (error) {
        console.log('Backend health check failed:', error.message);
        return false;
    }
}

// Event Listeners
function initEventListeners() {
    getTranscriptBtn.addEventListener('click', handleGetTranscript);
    youtubeUrlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleGetTranscript();
    });
    copyBtn.addEventListener('click', copyTranscriptToClipboard);
    downloadBtn.addEventListener('click', downloadTranscript);
    fontSizeSelect.addEventListener('change', (e) => {
        setFontSize(e.target.value);
        saveFontSizePreference(e.target.value);
    });
    languageSelect.addEventListener('change', handleLanguageChange);
    changeLanguageBtn.addEventListener('click', () => {
        if (currentVideoId && languageSelect.value) {
            fetchTranscriptWithLanguage(youtubeUrlInput.value, languageSelect.value);
        }
    });
}

// Get and display transcript
async function handleGetTranscript() {
    const url = youtubeUrlInput.value.trim();
    
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }
    
    if (!isValidYoutubeUrl(url)) {
        showError('Please enter a valid YouTube URL');
        // Track invalid URL submission if Analytics is available
        safeAnalyticsCall('trackUrlSubmission', url);
        return;
    }
    
    showLoading();
    // Track valid URL submission if Analytics is available
    safeAnalyticsCall('trackUrlSubmission', url);
    
    // Reset language selection
    resetLanguageSelection();
    
    // Save current video ID
    currentVideoId = extractVideoId(url);
    console.log('🔍 Processing video ID:', currentVideoId);
    
    try {
        // Fetch available languages first
        console.log('🔍 Starting language fetch process');
        const languagesResult = await fetchAvailableLanguages(url);
        availableLanguages = languagesResult || [];
        console.log('🔍 Languages fetch complete, count:', availableLanguages.length);
        
        // Sort languages to prioritize manual transcripts and then by name
        if (availableLanguages.length > 0) {
            availableLanguages.sort((a, b) => {
                // First prioritize manual transcripts
                if (a.type === 'manual' && b.type !== 'manual') return -1;
                if (a.type !== 'manual' && b.type === 'manual') return 1;
                // Then sort by name
                return a.name.localeCompare(b.name);
            });
        }
        
        // If no languages available, try default fetch
        if (availableLanguages.length === 0) {
            console.log('🔍 No languages found, trying default fetch');
            currentLanguage = null;
            const transcript = await fetchTranscript(url);
            displayTranscript(transcript);
            safeAnalyticsCall('trackTranscriptFetch', true, currentVideoId);
            return;
        }
        
        // Set current language to first available language only if user hasn't explicitly chosen one
        if (!currentLanguage || !availableLanguages.some(lang => lang.code === currentLanguage)) {
            currentLanguage = availableLanguages[0].code;
            console.log('🔍 Setting current language to first available:', currentLanguage);
        } else {
            console.log('🔍 Retaining user-selected language:', currentLanguage);
        }
        
        // Fetch transcript with the selected language
        const transcript = await fetchTranscript(url, currentLanguage);
        displayTranscript(transcript);
        safeAnalyticsCall('trackTranscriptFetch', true, currentVideoId, null, currentLanguage);
    } catch (error) {
        console.error('Error fetching transcript:', error);
        // Log the full error for debugging
        if (CONFIG.debug) {
            console.debug('Detailed error:', error);
        }
        
        // Get error message from the API response if available
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
        safeAnalyticsCall('trackTranscriptFetch', false, currentVideoId, errorMessage);
    }
}

// Extract video ID from YouTube URL
function extractVideoId(url) {
    const match = url.match(/(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : 'unknown';
}

// Validate YouTube URL
function isValidYoutubeUrl(url) {
    // More permissive regex for YouTube URLs
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})([&?].*)?$/;
    const isValid = youtubeRegex.test(url);
    
    // Debug info
    console.log('URL validation:', {
        url,
        isValid,
        match: url.match(youtubeRegex)
    });
    
    return isValid;
}

// Fetch transcript from API
async function fetchTranscript(url, language = null) {
    const apiUrl = CONFIG.apiUrl;
    
    // Log the current CONFIG state to help with debugging
    if (CONFIG.debug) {
        console.log('Current CONFIG state:', {
            apiUrl: CONFIG.apiUrl,
            apiKey: CONFIG.apiKey ? 'Set (not showing for security)' : 'NOT SET',
            debug: CONFIG.debug
        });
        console.log('Fetching transcript for URL:', url);
        console.log('Using API endpoint:', apiUrl);
        if (language) {
            console.log('Language selected:', language);
        }
    }
    
    // Ensure API key is set
    if (!CONFIG.apiKey) {
        console.error('API key is not set! Check CONFIG initialization.');
        throw new Error('Configuration error: API key is not set');
    }
    
    try {
        const payload = { url };
        if (language) {
            payload.language = language;
            console.log('🔍 Adding language to API request:', language);
        }
        
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
        
        // At this point, we have a successful transcript
        // Update current language if specified
        if (language) {
            currentLanguage = language;
        }
        
        return data.transcript;
    } catch (error) {
        if (CONFIG.debug) {
            console.error('Fetch error:', error);
        }
        throw error;
    }
}

// Fetch available languages for a video
async function fetchAvailableLanguages(url) {
    const apiUrl = `${CONFIG.languagesApiUrl}?url=${encodeURIComponent(url)}`;
    
    // Force debug logging for language fetching
    console.log('🔍 Fetching available languages for URL:', url);
    console.log('🔍 Using API endpoint:', apiUrl);
    
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('🔍 Languages API response status:', response.status);
        
        if (!response.ok) {
            console.error('❌ Failed to fetch languages, status:', response.status);
            // Don't throw here, just return empty languages list
            resetLanguageSelection();
            return [];
        }
        
        const data = await response.json();
        console.log('🔍 Languages API response data:', data);
        
        // Handle different response statuses
        if (data.status === 'success' || data.status === 'fallback') {
            const languages = data.languages || [];
            
            // Show note if it's a fallback response
            if (data.status === 'fallback' && data.note) {
                console.log('ℹ️ Languages fallback:', data.note);
            }
            
            console.log('🔍 Available languages:', languages);
            console.log('🔍 Number of languages:', languages.length);
            
            if (languages.length > 1) {
                // Multiple languages - show selection UI
                console.log('🔍 Multiple languages found, showing selection UI');
                populateLanguageDropdown(languages);
                showLanguageSelection();
            } else if (languages.length === 1) {
                // Single language - no need for selection UI
                console.log('🔍 Single language found, hiding selection UI');
                currentLanguage = languages[0].language_code;
                hideLanguageSelection();
            } else {
                // No languages available
                console.log('🔍 No languages found, hiding selection UI');
                hideLanguageSelection();
            }
            
            return languages;
        } else if (data.status === 'no_transcripts') {
            // Video has no transcripts available
            console.log('ℹ️ No transcripts available for this video:', data.note);
            
            // Show an informative message to the user
            const resultDiv = document.getElementById('transcript-result');
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div class="error-message">
                        <h3>No Transcripts Available</h3>
                        <p>${data.note || 'This video does not have any transcripts or subtitles available.'}</p>
                        <p>This could be because:</p>
                        <ul>
                            <li>The video creator disabled captions</li>
                            <li>No auto-generated captions are available</li>
                            <li>The video is too new and captions haven't been processed yet</li>
                        </ul>
                        <p>Try a different video that has captions enabled.</p>
                    </div>
                `;
            }
            
            hideLanguageSelection();
            return [];
        } else {
            // Error response
            console.error('❌ Languages API error:', data.error);
            resetLanguageSelection();
            return [];
        }
    } catch (error) {
        if (CONFIG.debug) {
            console.error('Error fetching languages:', error);
        }
        // Don't throw here, just return empty languages list
        resetLanguageSelection();
        return [];
    }
}

// Fetch transcript with a specific language
async function fetchTranscriptWithLanguage(url, language) {
    showLoading();
    
    console.log('🔍 Fetching transcript with specific language:', language);
    
    try {
        // Explicitly set the current language before fetching
        currentLanguage = language;
        console.log('🔍 Set current language to:', currentLanguage);
        
        // First make sure the API knows about this language
        console.log('🔍 Checking if language is available:', language);
        const languageExists = availableLanguages.some(lang => lang.code === language);
        
        if (!languageExists) {
            console.warn('⚠️ Selected language is not in available languages list!');
            // We'll continue anyway as the backend may still handle it
        }
        
        // Force debug output for this request
        console.log('🔍 Sending API request with URL:', url);
        console.log('🔍 Requesting language:', language);
        
        const transcript = await fetchTranscript(url, language);
        
        // Update the current transcript and redisplay
        currentTranscript = transcript;
        
        console.log('🔍 Got transcript with length:', transcript.length);
        console.log('🔍 First 100 chars:', transcript.substring(0, 100));
        
        // Force update the UI with the new transcript
        // Note: We don't call displayTranscript() here because it recreates the language UI
        // Instead, we just update the transcript content while preserving the language selection
        updateTranscriptContent(transcript);
        
        console.log('🔍 Transcript fetched successfully in language:', language);
        safeAnalyticsCall('trackTranscriptFetch', true, currentVideoId, null, language);
    } catch (error) {
        console.error('Error fetching transcript with language:', error);
        
        let errorMessage = 'Failed to get transcript in selected language.';
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
        safeAnalyticsCall('trackTranscriptFetch', false, currentVideoId, errorMessage, language);
    }
}

// Handle language selection change
function handleLanguageChange() {
    const selectedLanguage = languageSelect.value;
    
    if (selectedLanguage) {
        changeLanguageBtn.disabled = false;
        
        if (CONFIG.debug) {
            console.log('Language selected:', selectedLanguage);
        }
        
        // Track language selection
        safeAnalyticsCall('trackLanguageChange', selectedLanguage, currentVideoId);
    } else {
        changeLanguageBtn.disabled = true;
    }
}

// Populate language dropdown with available languages
function populateLanguageDropdown(languages) {
    // Clear current options
    languageSelect.innerHTML = '';
    
    console.log('🔍 Populating language dropdown with', languages.length, 'languages');
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select language...';
    languageSelect.appendChild(defaultOption);
    
    // Sort languages by name
    languages.sort((a, b) => a.language.localeCompare(b.language));
    
    // Track if we have at least one language to select by default
    let firstLanguageCode = null;
    
    // Add language options
    languages.forEach((lang, index) => {
        const option = document.createElement('option');
        option.value = lang.language_code;
        
        // Mark manual transcripts with a star (non-generated)
        const isManual = !lang.is_generated;
        option.textContent = isManual ? `${lang.language} ★` : lang.language;
        
        // Mark auto-generated transcripts with a class for styling
        if (lang.is_generated) {
            option.classList.add('auto-generated');
        }
        
        // Remember the first language code
        if (index === 0) {
            firstLanguageCode = lang.language_code;
        }
        
        languageSelect.appendChild(option);
    });
    
    // Enable the select element
    languageSelect.disabled = false;
    
    // Select the current language if it exists and is available, otherwise select the first language
    if (currentLanguage && languages.some(lang => lang.language_code === currentLanguage)) {
        languageSelect.value = currentLanguage;
        changeLanguageBtn.disabled = false;
        console.log('🔍 Language dropdown set to current language:', currentLanguage);
    } else if (firstLanguageCode) {
        languageSelect.value = firstLanguageCode;
        changeLanguageBtn.disabled = false;
        console.log('🔍 Language dropdown set to first language:', firstLanguageCode);
    }
    
    console.log('🔍 Language dropdown populated, selected language:', languageSelect.value);
}

// Show language selection UI
function showLanguageSelection() {
    console.log('🔍 Showing language selection UI');
    console.log('🔍 Before showing, language selection has classes:', languageSelection.className);
    
    // Force remove hidden class and apply any needed styles
    languageSelection.style.display = 'flex';
    languageSelection.classList.remove('hidden');
    
    // Add a distinct border to make it more visible
    languageSelection.style.borderColor = '#ff0000';
    
    console.log('🔍 After showing, language selection has classes:', languageSelection.className);
    console.log('🔍 Language selection display style:', languageSelection.style.display);
    
    // Make button obvious for testing
    changeLanguageBtn.style.backgroundColor = '#f9ca24';
    changeLanguageBtn.style.color = '#000000';
    changeLanguageBtn.style.fontWeight = 'bold';
}

// Hide language selection UI
function hideLanguageSelection() {
    console.log('🔍 Hiding language selection UI');
    console.log('🔍 Before hiding, language selection has classes:', languageSelection.className);
    
    languageSelection.classList.add('hidden');
    // Additional force hide
    languageSelection.style.display = 'none';
    
    console.log('🔍 After hiding, language selection has classes:', languageSelection.className);
    console.log('🔍 Language selection display style:', languageSelection.style.display);
}

// Reset language selection
function resetLanguageSelection() {
    availableLanguages = [];
    currentLanguage = null;
    languageSelect.innerHTML = '<option value="">Loading languages...</option>';
    languageSelect.disabled = true;
    changeLanguageBtn.disabled = true;
    hideLanguageSelection();
}

// Update only the transcript content without recreating language UI
function updateTranscriptContent(transcript) {
    hideLoading();
    
    console.log('🔍 updateTranscriptContent called with currentLanguage:', currentLanguage);
    
    if (!transcript) {
        showError('No transcript found for this video');
        return;
    }
    
    // Save current transcript for later use
    currentTranscript = transcript;
    
    // Split transcript into paragraphs
    const formattedTranscript = formatTranscript(transcript);
    
    // Display transcript
    transcriptContent.innerHTML = formattedTranscript;
    
    // Update the language dropdown selection to reflect the current language
    const transcriptSelect = document.getElementById('transcript-language-select');
    if (transcriptSelect && currentLanguage) {
        transcriptSelect.value = currentLanguage;
        console.log('🔍 Updated transcript dropdown to:', currentLanguage);
        console.log('🔍 Dropdown now shows:', transcriptSelect.options[transcriptSelect.selectedIndex]?.text);
    }
    
    // Show transcript container
    errorMessage.classList.add('hidden');
    transcriptContainer.classList.remove('hidden');
    
    // Apply font size
    setFontSize(getFontSizePreference());
    
    // Scroll to transcript
    transcriptContainer.scrollIntoView({ behavior: 'smooth' });
}

// Format and display transcript
function displayTranscript(transcript) {
    hideLoading();
    
    console.log('🔍 displayTranscript called with currentLanguage:', currentLanguage);
    console.log('🔍 Available languages count:', availableLanguages.length);
    
    if (!transcript) {
        showError('No transcript found for this video');
        return;
    }
    
    // Save current transcript for later use
    currentTranscript = transcript;
    
    // Split transcript into paragraphs
    const formattedTranscript = formatTranscript(transcript);
    
    // Display transcript
    transcriptContent.innerHTML = formattedTranscript;
    
    console.log('🔍 Handling language selection in transcript display');
    console.log('🔍 Available languages count:', availableLanguages.length);
    console.log('🔍 Current language:', currentLanguage);
        
    // Show language selection if any languages are available (even just one)
    if (availableLanguages.length > 0) {
        console.log('🔍 Languages available, adding language selector to transcript controls');
        console.log('🔍 Languages:', availableLanguages.map(l => `${l.name} (${l.code})`));
        
        // First, ensure the original language selection is completely hidden
        if (languageSelection) {
            languageSelection.style.display = 'none';
            languageSelection.classList.add('hidden');
            // Apply !important to ensure it stays hidden
            languageSelection.setAttribute('style', 'display: none !important');
        }
        
        // Create a new language selection UI in the transcript controls
        const langSelectionClone = document.createElement('div');
        langSelectionClone.id = 'transcript-lang-selection';
        langSelectionClone.className = 'language-selection';
        langSelectionClone.style.display = 'flex';
        
        // Create the internal structure (language selector and button)
        const selectorDiv = document.createElement('div');
        selectorDiv.className = 'language-selector';
        
        const label = document.createElement('label');
        label.textContent = 'Language:';
        label.htmlFor = 'transcript-language-select';
        
        const select = document.createElement('select');
        select.id = 'transcript-language-select';
        
        // Populate the select with language options
        console.log('🔍 Creating transcript dropdown with currentLanguage:', currentLanguage);
        availableLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            // Mark manual transcripts with a star
            const isManual = lang.type === 'manual';
            option.textContent = isManual ? `${lang.name} ★` : lang.name;
            
            // If this is the current language, mark it as selected
            if (lang.code === currentLanguage) {
                option.selected = true;
                console.log('🔍 Setting option as selected:', lang.name, '(', lang.code, ')');
            }
            
            select.appendChild(option);
        });
        
        console.log('🔍 Final select value:', select.value);
        console.log('🔍 Selected option text:', select.options[select.selectedIndex]?.text);
        
        const button = document.createElement('button');
        button.id = 'transcript-change-language-btn';
        button.className = 'secondary-btn';
        button.innerHTML = '<i class="fas fa-language"></i> Get Language Transcript';
        
        // Assemble the components
        selectorDiv.appendChild(label);
        selectorDiv.appendChild(select);
        langSelectionClone.appendChild(selectorDiv);
        langSelectionClone.appendChild(button);
        
        // Clear previous content and add the clone
        transcriptLanguageSelection.innerHTML = '';
        transcriptLanguageSelection.appendChild(langSelectionClone);
        
        // Make the transcript language selection container visible
        transcriptLanguageSelection.style.display = 'block';
        
        // Set up event listeners for the transcript language selection
        const transcriptSelect = document.getElementById('transcript-language-select');
        const transcriptChangeBtn = document.getElementById('transcript-change-language-btn');
        
        console.log('🔍 Transcript select found:', !!transcriptSelect);
        console.log('🔍 Transcript change button found:', !!transcriptChangeBtn);
        
        if (transcriptSelect && transcriptChangeBtn) {
            // Enable/disable button based on current selection
            transcriptChangeBtn.disabled = !transcriptSelect.value;
            
            // Highlight the button to make it more noticeable
            transcriptChangeBtn.style.backgroundColor = '#f9ca24';
            transcriptChangeBtn.style.fontWeight = 'bold';
            
            // Remove any existing event listeners to prevent duplicates
            const newSelect = transcriptSelect.cloneNode(true);
            transcriptSelect.parentNode.replaceChild(newSelect, transcriptSelect);
            
            const newBtn = transcriptChangeBtn.cloneNode(true);
            transcriptChangeBtn.parentNode.replaceChild(newBtn, transcriptChangeBtn);
            
            // Re-select the elements
            const freshSelect = document.getElementById('transcript-language-select');
            const freshBtn = document.getElementById('transcript-change-language-btn');
            
            freshSelect.addEventListener('change', function() {
                console.log('🔍 Transcript language selection changed to:', this.value);
                
                // Enable/disable button based on selection
                freshBtn.disabled = !this.value;
                
                // Track language selection
                if (this.value) {
                    safeAnalyticsCall('trackLanguageChange', this.value, currentVideoId);
                }
            });
            
            freshBtn.addEventListener('click', function() {
                const selectedLang = freshSelect.value;
                if (currentVideoId && selectedLang) {
                    console.log('🔍 Changing transcript language to:', selectedLang);
                    fetchTranscriptWithLanguage(youtubeUrlInput.value, selectedLang);
                }
            });
        }
    } else {
        // Clear the transcript language selection area if no language options
        transcriptLanguageSelection.innerHTML = '';
    }
    
    // Show transcript container
    errorMessage.classList.add('hidden');
    transcriptContainer.classList.remove('hidden');
    
    // Apply font size
    setFontSize(getFontSizePreference());
    
    // Scroll to transcript
    transcriptContainer.scrollIntoView({ behavior: 'smooth' });
}

// Format transcript with paragraphs, speaker labels, etc.
function formatTranscript(transcript) {
    // Split the transcript into lines
    const lines = transcript.split('\n');
    let formattedHtml = '';
    
    // Process each line
    lines.forEach(line => {
        if (!line.trim()) return; // Skip empty lines
        
        // Check for timestamp format [MM:SS]
        const timestampMatch = line.match(/^\[(\d+:\d+)\]\s*(.*)/);
        
        if (timestampMatch) {
            // const timestamp = timestampMatch[1]; // Not needed since we're not showing timestamps
            let content = timestampMatch[2].trim();
            
            // Create HTML for this line
            let lineHtml = '<p>';
            
            // No timestamps shown - don't add the timestamp span
            
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
        showCopyNotification();
        safeAnalyticsCall('trackCopyAction');
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

// Download transcript as a text file
function downloadTranscript() {
    if (!currentTranscript) return;
    
    // Create a filename with video ID and language if available
    let filename = `transcript_${currentVideoId}`;
    if (currentLanguage) {
        filename += `_${currentLanguage}`;
    }
    filename += '.txt';
    
    // Create a blob with the transcript text
    const blob = new Blob([currentTranscript], { type: 'text/plain;charset=utf-8' });
    
    // Create a URL for the blob
    const url = URL.createObjectURL(blob);
    
    // Create a temporary anchor element to trigger the download
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    
    // Trigger the download
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
    
    // Track download event
    safeAnalyticsCall('trackDownloadAction', currentLanguage);
}

// Set font size
function setFontSize(size) {
    if (!size || !['small', 'medium', 'large'].includes(size)) {
        size = DEFAULT_FONT_SIZE;
    }
    transcriptContent.className = `content-area font-${size}`;
    fontSizeSelect.value = size;
    
    // Track font size change if Analytics is available
    safeAnalyticsCall('trackFontSizeChange', size);
}

// Helper functions
function showLoading() {
    loadingIndicator.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    transcriptContainer.classList.add('hidden');
}

function hideLoading() {
    console.log('🔍 hideLoading() called');
    loadingIndicator.classList.add('hidden');
    console.log('🔍 Loading indicator hidden');
}

function showError(message) {
    hideLoading();
    transcriptContainer.classList.add('hidden');
    errorMessage.classList.remove('hidden');
    errorText.textContent = message;
}

function showCopyNotification() {
    copyNotification.classList.remove('hidden');
}

function hideCopyNotification() {
    copyNotification.classList.add('hidden');
}

// Helper function to safely call Analytics methods
function safeAnalyticsCall(methodName, ...args) {
    if (typeof Analytics !== 'undefined' && Analytics && typeof Analytics[methodName] === 'function') {
        try {
            Analytics[methodName](...args);
        } catch (error) {
            console.debug('Analytics call failed:', error);
        }
    }
}

// Helper function to test the Gangnam Style video directly
function testGangnamStyle() {
    console.log('🧪 Testing Gangnam Style video');
    youtubeUrlInput.value = 'https://www.youtube.com/watch?v=9bZkp7q19f0';
    
    // Use a small timeout to simulate a real click
    setTimeout(() => {
        console.log('🧪 Triggering Get Transcript button click');
        getTranscriptBtn.click();
    }, 100);
    
    return 'Gangnam Style test initiated - check console for progress';
}

// Add this to the window object so it can be called from the console
window.testGangnamStyle = testGangnamStyle;

// Helper functions for testing - these will be available in the console
function testLanguageDropdown() {
    console.log('🧪 Running language dropdown test');
    
    // Check if elements exist
    console.log('🧪 Language selection element exists:', !!languageSelection);
    console.log('🧪 Language select element exists:', !!languageSelect);
    console.log('🧪 Change language button exists:', !!changeLanguageBtn);
    
    // Get computed styles
    const selectionStyle = window.getComputedStyle(languageSelection);
    console.log('🧪 Language selection computed display:', selectionStyle.display);
    console.log('🧪 Language selection computed visibility:', selectionStyle.visibility);
    console.log('🧪 Language selection has hidden class:', languageSelection.classList.contains('hidden'));
    
    // Test toggle
    console.log('🧪 Testing toggle of language selection');
    
    // Force show
    languageSelection.style.display = 'flex';
    languageSelection.classList.remove('hidden');
    console.log('🧪 After force show - display:', languageSelection.style.display);
    console.log('🧪 After force show - has hidden class:', languageSelection.classList.contains('hidden'));
    
    // Create some mock language data
    const mockLanguages = [
        { code: 'en', name: 'English', type: 'manual' },
        { code: 'es', name: 'Spanish', type: 'auto' },
        { code: 'fr', name: 'French', type: 'auto' }
    ];
    
    // Test populating dropdown
    populateLanguageDropdown(mockLanguages);
    console.log('🧪 Dropdown populated with mock data');
    console.log('🧪 Dropdown has options:', languageSelect.options.length);
    
    return 'Language dropdown test complete - check console for results';
}

// Add this to the window object so it can be called from the console
window.testLanguageDropdown = testLanguageDropdown;

// Local Storage Preferences
function saveFontSizePreference(size) {
    localStorage.setItem('transcriptFontSize', size);
}

function getFontSizePreference() {
    return localStorage.getItem('transcriptFontSize') || DEFAULT_FONT_SIZE;
}
