import requests
import streamlit as st
import os
from src.utils.decorators import timeout

@timeout(30)
def get_recipes_from_spoonacular(ingredients, max_recipes=4):
    """Fetch recipes from Spoonacular API based on ingredients."""
    try:
        api_key = os.getenv("SPOONACULAR_API_KEY")
        base_url = "https://api.spoonacular.com/recipes/findByIngredients"
        
        params = {
            "apiKey": api_key,
            "ingredients": ",".join(ingredients),
            "number": max_recipes,
            "ranking": 2,  # Maximize used ingredients
            "ignorePantry": True
        }
        
        response = requests.get(base_url, params=params)
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
        return []
    except Exception as e:
        st.error(f"Unexpected error in recipe service: {str(e)}")
        return []