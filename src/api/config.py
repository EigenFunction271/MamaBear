import os

SPOONACULAR_BASE_URL = "https://api.spoonacular.com"
GROQ_MODEL = "mixtral-8x7b-32768"

def get_api_config():
    """Get API configuration and endpoints."""
    return {
        "spoonacular": {
            "base_url": SPOONACULAR_BASE_URL,
            "api_key": os.getenv("SPOON