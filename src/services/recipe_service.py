import requests
import streamlit as st
import os
from src.utils.decorators import timeout
from src.utils.streamlit_context import with_streamlit_context
import logging
from groq import Groq
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class RecipeService:
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize API clients with fallback options."""
        # Try Groq first
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                logger.debug("Initializing Groq client...")
                self.groq_client = Groq(api_key=groq_key)
                # Test connection
                self._test_groq_connection()
                logger.info("Successfully initialized Groq client")
            else:
                logger.warning("No Groq API key found")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {str(e)}")
            self.groq_client = None

        # Initialize OpenAI as fallback
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                logger.debug("Initializing OpenAI client...")
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("Successfully initialized OpenAI client")
            else:
                logger.warning("No OpenAI API key found")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {str(e)}")
            self.openai_client = None

    def _test_groq_connection(self):
        """Test Groq API connection."""
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "system", "content": "Test"}],
                model="mixtral-8x7b-32768",
                max_tokens=10
            )
            if not response:
                raise ValueError("Empty response from Groq")
        except Exception as e:
            logger.error(f"Groq connection test failed: {str(e)}")
            raise

    def get_recipe_details(self, recipe_name: str) -> str:
        """Get recipe details using available AI models with fallback."""
        prompt = f"""
        Generate a detailed recipe for "{recipe_name}" with:
        - Estimated cooking time
        - Difficulty level
        - Key steps
        """

        # Try Groq first
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful culinary assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model="mixtral-8x7b-32768",
                    max_tokens=200,
                    temperature=0.7
                )
                if response and response.choices:
                    return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API error: {str(e)}")

        # Fallback to OpenAI
        if self.openai_client:
            try:
                logger.info("Falling back to OpenAI API")
                response = self.openai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful culinary assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model="gpt-3.5-turbo",
                    max_tokens=200,
                    temperature=0.7
                )
                if response and response.choices:
                    return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")

        logger.error("All API attempts failed")
        return None

@timeout(30)
@with_streamlit_context
def get_recipes_from_spoonacular(ingredients, max_recipes=4):
    """Fetch recipes from Spoonacular API based on ingredients."""
    try:
        api_key = os.getenv("SPOONACULAR_API_KEY")
        base_url = "https://api.spoonacular.com/recipes/findByIngredients"
        
        # Add logging to debug API key
        logger.debug(f"Using Spoonacular API key: {api_key[:5]}...")  # Only log first 5 chars for security
        
        params = {
            "apiKey": api_key,
            "ingredients": ",".join(ingredients),
            "number": max_recipes,
            "ranking": 2,  # Maximize used ingredients
            "ignorePantry": True
        }
        
        response = requests.get(base_url, params=params)
        
        # Add more detailed error handling
        if response.status_code == 401:
            st.error("Invalid Spoonacular API key. Please check your .env file.")
            logger.error("Spoonacular API authentication failed")
            return []
        elif response.status_code == 402:
            st.error("Spoonacular API quota exceeded")
            logger.error("Spoonacular API quota exceeded")
            return []
            
        response.raise_for_status()
        recipes = response.json()
        
        # Filter out recipes with no images or titles
        valid_recipes = [
            recipe for recipe in recipes 
            if recipe.get('image') and recipe.get('title')
        ]
        
        return valid_recipes

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recipes: {str(e)}")
        logger.error(f"Spoonacular API request failed: {str(e)}")
        return []