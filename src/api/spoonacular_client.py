import requests
import os
import logging
from typing import Dict, List, Optional
import streamlit as st
from src.utils.decorators import timeout

logger = logging.getLogger(__name__)

class SpoonacularClient:
    def __init__(self):
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("SPOONACULAR_API_KEY not found in environment variables")
        self.base_url = "https://api.spoonacular.com"

    @timeout(30)
    def get_recipes_by_ingredients(
        self, 
        ingredients: List[str], 
        max_recipes: int = 4,
        offset: int = 0
    ) -> List[Dict]:
        endpoint = f"{self.base_url}/recipes/findByIngredients"
        
        params = {
            "apiKey": self.api_key,
            "ingredients": ",".join(ingredients),
            "number": max_recipes,
            "ranking": 2,
            "ignorePantry": True,
            "offset": offset
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Spoonacular API error: {str(e)}")
            return []

    @timeout(30)
    def get_recipe_information(
        self, 
        recipe_id: int,
        include_nutrition: bool = True
    ) -> Optional[Dict]:
        endpoint = f"{self.base_url}/recipes/{recipe_id}/information"
        
        params = {
            "apiKey": self.api_key,
            "includeNutrition": include_nutrition
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recipe details: {str(e)}")
            return None

# Initialize a single client instance
_client: Optional[SpoonacularClient] = None

def get_client() -> SpoonacularClient:
    global _client
    if _client is None:
        _client = SpoonacularClient()
    return _client

@timeout(30)
def get_recipes_from_spoonacular(ingredients: List[str], max_recipes: int = 4, offset: int = 0) -> List[Dict]:
    client = get_client()
    return client.get_recipes_by_ingredients(ingredients, max_recipes, offset)

@timeout(30)
def get_recipe_information(recipe_id: int) -> Dict:
    client = get_client()
    return client.get_recipe_information(recipe_id) or {}

def initialize_spoonacular_client() -> SpoonacularClient:
    return get_client()

# Export all needed functions
__all__ = [
    'get_recipes_from_spoonacular',
    'get_recipe_information',
    'initialize_spoonacular_client'
]