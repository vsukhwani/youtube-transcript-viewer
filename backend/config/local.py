# Configuration for local development environment

# API Settings
API_PORT = 3002
DEBUG = True

# Security Settings
API_KEY = "dev_api_key_1234567890"  # Development API key
VERIFY_API_KEY = True  # Set to True to enable API key verification
ALLOWED_REFERRERS = ["*"]  # Allow all referrers in development

# CORS Settings
CORS_ALLOW_ORIGINS = "*"  # Allow all origins in development
CORS_ALLOW_METHODS = "GET, POST, OPTIONS"
CORS_ALLOW_HEADERS = "Content-Type, X-API-Key, Origin, Referer"

# Logging
LOG_LEVEL = "INFO"

# Rate Limiting (requests per minute per IP)
RATE_LIMIT = 0  # No rate limiting in development

# Security
DETAILED_ERRORS = True  # Show detailed errors in development
