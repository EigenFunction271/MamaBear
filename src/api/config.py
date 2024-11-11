import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def load_environment():
    """Load and validate all environment variables."""
    load_dotenv()
    
    # Check required API keys
    required_keys = [
        "SPOONACULAR_API_KEY",
        "GOOGLE_CLOUD_API_KEY"
    ]
    
    # Optional API keys
    optional_keys = [
        "GROQ_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_keys = []
    api_config = {}
    
    # Check required keys
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        else:
            logger.info(f"Found {key}: {value[:6]}...")
            api_config[key.lower()] = value
    
    # Check optional keys
    for key in optional_keys:
        value = os.getenv(key)
        if value:
            logger.info(f"Found optional {key}: {value[:6]}...")
            api_config[key.lower()] = value
        else:
            logger.warning(f"Optional {key} not found")
            
    if missing_keys:
        logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return api_config 