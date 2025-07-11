import os
import importlib.util
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "API_PORT": 3002,
    "DEBUG": False,
    "API_KEY": "default_api_key_do_not_use_in_production",
    "VERIFY_API_KEY": True,
    "ALLOWED_REFERRERS": ["localhost:3002"],
    "CORS_ALLOW_ORIGINS": "*",
    "CORS_ALLOW_METHODS": "POST, OPTIONS",
    "CORS_ALLOW_HEADERS": "Content-Type, X-API-Key, Origin, Referer",
    "LOG_LEVEL": "INFO",
    "RATE_LIMIT": 60,
    "DETAILED_ERRORS": False,
}

def load_config():
    """
    Load configuration based on the environment.
    If VERCEL_ENV is set, use production config.
    Otherwise, use local config or default if not found.
    """
    # Determine which config file to load
    env = os.environ.get("VERCEL_ENV", "local")
    config_path = os.path.join(os.path.dirname(__file__), f"{env}.py")
    
    # Initialize with default config
    config = DEFAULT_CONFIG.copy()
    
    # Try to load environment-specific config
    if os.path.exists(config_path):
        try:
            spec = importlib.util.spec_from_file_location("config", config_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Update config with environment-specific values
            for key in DEFAULT_CONFIG:
                if hasattr(module, key):
                    config[key] = getattr(module, key)
            
            logger.info(f"Loaded configuration for environment: {env}")
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
            logger.warning("Using default configuration")
    else:
        logger.warning(f"Config file not found: {config_path}")
        logger.warning("Using default configuration")
    
    # Override with environment variables if they exist
    if os.environ.get("API_KEY"):
        config["API_KEY"] = os.environ.get("API_KEY")
        logger.info("Using API key from environment variable")
    
    # Set log level based on config
    log_level = getattr(logging, config["LOG_LEVEL"], logging.INFO)
    logging.getLogger().setLevel(log_level)
    
    return config

# Load and export config
config = load_config()
