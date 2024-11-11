import warnings
warnings.filterwarnings('ignore', message='.*missing ScriptRunContext.*')

import streamlit as st
from dotenv import load_dotenv
import os
from src.utils.image_processing import process_image
from src.api.groq_client import initialize_groq_client
from src.api.spoonacular_client import initialize_spoonacular_client
from src.api.gemini_client import initialize_gemini_client
from src.services.image_analysis_service import analyze_fridge_image
from src.services.recipe_service import get_recipes_from_spoonacular
from src.ui.components import create_recipe_card
from src.pages.meal_planner_page import render_meal_planner_page
from src.pages.home_page import render_home_page
from src.pages.recipe_page import render_recipe_page, display_recipes, generate_recipe_details

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

def initialize_apis():
    """Initialize API clients and check environment variables."""
    load_dotenv()
    
    required_vars = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "SPOONACULAR_API_KEY": os.getenv("SPOONACULAR_API_KEY")
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
        st.error(error_msg)
        raise ValueError(error_msg)
    
    return {
        'groq': initialize_groq_client(),
        'spoonacular': initialize_spoonacular_client(),
        'gemini': initialize_gemini_client()
    }

def main():
    """Main application function with Streamlit UI."""
    try:
        st.set_page_config(layout="wide", page_title="MamaBear")
        
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = "Home"
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        st.sidebar.page_link = st.sidebar.radio(
            "Go to",
            ["Home", "Recipe Analysis", "Meal Planning"]
        )
        
        # Initialize APIs
        apis = initialize_apis()
        
        # Page routing
        if st.sidebar.page_link == "Home":
            render_home_page()
        elif st.sidebar.page_link == "Recipe Analysis":
            render_recipe_page(apis)
        elif st.sidebar.page_link == "Meal Planning":
            render_meal_planner_page(st.session_state.get('selected_recipe'))
    except Exception as e:
        st.error("😔 Something went wrong!")
        st.error(str(e))
        if st.button("🔄 Restart Application"):
            st.rerun()

if __name__ == "__main__":
    main()


