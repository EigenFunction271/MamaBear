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

def display_recipes(items_info, groq_client):
    """Display recipe cards in a grid layout."""
    ingredients_key = tuple(sorted(items_info.keys()))
    
    with st.spinner("🔍 Searching for recipes..."):
        recipes = get_recipes_from_spoonacular(ingredients_key)
        
    if recipes:
        cols = st.columns(2)
        for idx, recipe in enumerate(recipes):
            with cols[idx % 2]:
                recipe_details = generate_recipe_details(groq_client, recipe)
                st.markdown(create_recipe_card(recipe, recipe_details), unsafe_allow_html=True)
    else:
        st.warning("No recipes found. Try with different ingredients.")

def main():
    """Main application function with Streamlit UI."""
    try:
        st.set_page_config(layout="wide", page_title="FoodEase")
        st.title("🍽️ FoodEase: AI Family Hub")
        
        with st.spinner("Initializing..."):
            apis = initialize_apis()
            
        st.markdown("""
        ### 📸 How to use:
        1. Upload a photo of your fridge contents
        2. Wait for AI analysis
        3. View detected items and recipe suggestions
        """)
        
        uploaded_file = st.file_uploader(
            "📸 Upload an image of your fridge", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of your fridge contents"
        )
        
        if uploaded_file:
            with st.spinner("🔍 Processing your image..."):
                temp_path = process_image(uploaded_file)
                if temp_path:
                    try:
                        analysis_result, annotated_image, items_info = analyze_fridge_image(temp_path)
                        
                        if analysis_result and items_info:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.image(annotated_image, caption="Analyzed Fridge Contents")
                            
                            with col2:
                                st.markdown("### 📝 Detected Items:")
                                st.write(analysis_result)
                            
                            st.markdown("### 🍳 Recommended Recipes")
                            display_recipes(items_info, apis['groq'])
                        else:
                            st.error("Could not analyze the image. Please try again with a clearer photo.")
                    finally:
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
    except Exception as e:
        st.error("😔 Something went wrong!")
        st.error(str(e))
        if st.button("🔄 Restart Application"):
            st.experimental_rerun()

if __name__ == "__main__":
    main()


