# Configuration for production environment (Vercel)

import os

# API Settings
API_PORT = 3000  # This won't be used in Vercel, but kept for reference
DEBUG = False

# Security Settings
API_KEY = os.environ.get("API_KEY", "REPLACE_WITH_SECURE_RANDOM_KEY_IN_VERCEL_ENV")  # Set as environment variable in Vercel
VERIFY_API_KEY = True  # Enable API key verification
ALLOWED_REFERRERS = [
    "*.vercel.app",
    "localhost",
    "127.0.0.1"
]  # Allow Vercel domains and localhost for testing

# CORS Settings
CORS_ALLOW_ORIGINS = "*"  # Allow all origins for standalone app, or specify your domain
CORS_ALLOW_METHODS = "GET, POST, OPTIONS"
CORS_ALLOW_HEADERS = "Content-Type, X-API-Key, Origin, Referer"

# Logging
LOG_LEVEL = "INFO"  # Use INFO for better debugging on Vercel

# Rate Limiting (requests per minute per IP)
RATE_LIMIT = 60  # Limit to 60 requests per minute in production

# Security
DETAILED_ERRORS = False  # Don't show detailed errors in production
