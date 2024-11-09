import requests
import os
from typing import Dict, List, Optional
import streamlit as st
from src.utils.decorators import timeout

class SpoonacularClient:
    def __init__(self):
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.base_url = "https://api.spoonacular.com"

    @timeout(30)
    def find_recipes_by_ingredients(
        self, 
        ingredients: List[str], 
        max_recipes: int = 4
    ) -> List[Dict]:
        """
        Find recipes based on available ingredients.
        
        Args:
            ingredients: List of ingredient names
            max_recipes: Maximum number of recipes to return
            
        Returns:
            List of recipe dictionaries
        """
        endpoint = f"{self.base_url}/recipes/findByIngredients"
        
        params = {
            "apiKey": self.api_key,
            "ingredients": ",".join(ingredients),
            "number": max_recipes,
            "ranking": 2,
            "ignorePantry": True
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Spoonacular API error: {str(e)}")
            return []

    @timeout(30)
    def get_recipe_information(
        self, 
        recipe_id: int
    ) -> Optional[Dict]:
        """
        Get detailed information about a specific recipe.
        
        Args:
            recipe_id: Spoonacular recipe ID
            
        Returns:
            Recipe information dictionary or None if error
        """
        endpoint = f"{self.base_url}/recipes/{recipe_id}/information"
        
        params = {
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching recipe details: {str(e)}")
            return None

def initialize_spoonacular_client() -> SpoonacularClient:
    """Initialize and return Spoonacular client."""
    try:
        return SpoonacularClient()
    except Exception as e:
        st.error(f"Failed to initialize Spoonacular client: {str(e)}")
        raise