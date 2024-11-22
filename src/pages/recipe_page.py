import streamlit as st
from src.utils.image_processing import process_image
from src.services.image_analysis_service import analyze_fridge_image
from src.services.recipe_service import get_recipes_from_spoonacular
from src.ui.components import create_recipe_card
from src.api.spoonacular_client import (
    get_recipes_from_spoonacular,
    get_recipe_information,
    initialize_spoonacular_client
)

@st.cache_resource
def preload_components():
    """Preload common components."""
    return {
        'recipe_card_css': """
            <style>
            .recipe-card { /* Your CSS here */ }
            </style>
        """,
        'common_prompts': {
            'recipe_analysis': "...",
            'cooking_instructions': "..."
        }
    }

def render_recipe_page(apis):
    """Render the recipe analysis and suggestion page."""
    # Preload components at start
    components = preload_components()
    st.markdown(components['recipe_card_css'], unsafe_allow_html=True)
    
    st.header("🔍 Recipe Analysis")
    
    # Initialize session state variables if they don't exist
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'current_annotated_image' not in st.session_state:
        st.session_state.current_annotated_image = None
    if 'current_items_info' not in st.session_state:
        st.session_state.current_items_info = None
    if 'current_recipes' not in st.session_state:
        st.session_state.current_recipes = None
    
    # Image upload section
    uploaded_file = st.file_uploader(
        "📸 Upload an image of your fridge", 
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of your fridge contents"
    )
    
    if uploaded_file:
        # Create a loading container with multiple status updates
        with st.status("Processing your image...", expanded=True) as status:
            st.write("Initializing analysis...")
            temp_path = process_image(uploaded_file)
            
            if temp_path:
                try:
                    # Update status for each major step
                    status.update(label="Analyzing image...", state="running")
                    st.write("🔍 Detecting items...")
                    analysis_result, annotated_image, items_info = analyze_fridge_image(temp_path)
                    
                    if analysis_result and items_info:
                        status.update(label="Storing results...", state="running")
                        st.write("💾 Saving analysis...")
                        # Store results in session state
                        st.session_state.current_analysis = analysis_result
                        st.session_state.current_annotated_image = annotated_image
                        st.session_state.current_items_info = items_info
                        
                        # Clear previous recipes
                        st.session_state.current_recipes = None
                        status.update(label="Analysis complete!", state="complete")
                finally:
                    try:
                        import os
                        os.remove(temp_path)
                    except:
                        pass
    
    # Display stored analysis results if they exist
    if st.session_state.current_analysis and st.session_state.current_annotated_image:
        # Display results in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(st.session_state.current_annotated_image, caption="Analyzed Fridge Contents")
        
        with col2:
            st.markdown("### 📝 Detected Items:")
            st.write(st.session_state.current_analysis)
        
        # Display recipe suggestions
        st.markdown("### 🍳 Recommended Recipes")
        display_recipes(st.session_state.current_items_info, apis['groq'])
        
        # Add meal planning button
        if st.button("📅 Plan These Meals"):
            st.session_state.page = "Meal Planning"

def display_recipes(items_info, groq_client):
    """Display recipe cards in a grid layout with lazy loading."""
    # Add custom CSS to reduce padding and margins
    st.markdown("""
        <style>
        .stExpander {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0px !important;
            margin: 0px !important;
        }
        .element-container {
            margin: 0px !important;
            padding: 0px !important;
        }
        .row-widget {
            margin: 0px !important;
            padding: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.current_recipes is None:
        ingredients_key = tuple(sorted(items_info.keys()))
        
        # Create a loading container for recipe search
        with st.status("Finding recipes...", expanded=True) as status:
            st.write("🔍 Searching recipe database...")
            recipes = get_recipes_from_spoonacular(ingredients_key, max_recipes=4)
            
            if recipes:
                st.write(f"✅ Found {len(recipes)} matching recipes!")
                st.session_state.current_recipes = recipes
                status.update(label="Recipes found!", state="complete")
            else:
                status.update(label="No recipes found", state="error")
    
    if st.session_state.current_recipes:
        # Add a progress bar for recipe card generation
        progress_text = "Generating recipe cards..."
        recipe_count = len(st.session_state.current_recipes)
        progress_bar = st.progress(0, text=progress_text)
        
        cols = st.columns(2)
        for idx, recipe in enumerate(st.session_state.current_recipes):
            with cols[idx % 2]:
                # Update progress
                progress = (idx + 1) / recipe_count
                progress_bar.progress(progress, text=f"Generating recipe {idx + 1} of {recipe_count}")
                
                # Get complete recipe information from Spoonacular
                recipe_details = get_recipe_information(recipe['id'])
                
                # Display recipe image and title
                st.image(recipe.get('image', ''), use_container_width=True)
                st.markdown(f"### {recipe['title']}")
                
                # Basic info in columns
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.markdown("🔥 **Calories:** " + 
                        (f"{recipe_details.get('nutrition', {}).get('nutrients', [{}])[0].get('amount', 'Not')} kcal" 
                         if recipe_details and 'nutrition' in recipe_details 
                         else "Not available"))
                    st.markdown("⏱️ **Time:** " + 
                        (f"{recipe_details.get('readyInMinutes', 'Not specified')} mins" 
                         if recipe_details 
                         else "Not specified mins"))
                    st.markdown("💰 **Price:** $" + 
                        (f"{recipe_details.get('pricePerServing', 'N/A')}/serving" 
                         if recipe_details 
                         else "N/A/serving"))
                
                with info_col2:
                    st.markdown("🥗 **Dietary:** " + 
                        (', '.join(recipe_details.get('diets', ['Not specified'])) 
                         if recipe_details and recipe_details.get('diets') 
                         else "Not specified"))
                    st.markdown("🌎 **Cuisine:** " + 
                        (', '.join(recipe_details.get('cuisines', ['Not specified'])) 
                         if recipe_details and recipe_details.get('cuisines') 
                         else "Not specified"))
                    st.markdown("📊 **Difficulty:** " + 
                        (get_difficulty_level(recipe_details) 
                         if recipe_details 
                         else "Not specified"))
                
                # Ingredients section
                st.markdown("#### 🧂 Ingredients")
                ing_col1, ing_col2 = st.columns(2)
                with ing_col1:
                    st.markdown("**Available:**\n" + 
                        ', '.join([ing['name'] for ing in recipe.get('usedIngredients', []) 
                                 if isinstance(ing, dict) and 'name' in ing]) or 'None')
                
                with ing_col2:
                    st.markdown("**Missing:**\n" + 
                        ', '.join([ing['name'] for ing in recipe.get('missedIngredients', []) 
                                 if isinstance(ing, dict) and 'name' in ing]) or 'None')
                
                # Instructions in compact expander
                with st.expander("📝 Instructions"):
                    st.markdown(recipe_details.get('instructions', 'Instructions not available'))
                
                # Schedule button
                if st.button(f"📅 Schedule {recipe['title']}", key=f"schedule_{recipe['id']}"):
                    st.session_state.selected_recipe = recipe_details
                    st.session_state.page = "Meal Planning"
                    st.rerun()
                
                # Add a small divider between recipes
                st.markdown("---")
        
        # Add "Load More" button centered at the bottom
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Load More Recipes", key="load_more"):
                with st.spinner("Finding more recipes..."):
                    more_recipes = get_recipes_from_spoonacular(
                        ingredients_key,
                        max_recipes=4,
                        offset=len(st.session_state.current_recipes)
                    )
                    if more_recipes:
                        st.session_state.current_recipes.extend(more_recipes)
                        st.rerun()
                    else:
                        st.info("No more recipes found with these ingredients.")
    else:
        st.warning("No recipes found. Try with different ingredients.")

def get_difficulty_level(recipe_details: dict) -> str:
    """Calculate difficulty level based on recipe attributes."""
    if not recipe_details:
        return "Not specified"
        
    # Calculate difficulty based on preparation time and number of ingredients
    prep_time = recipe_details.get('readyInMinutes', 0)
    ingredients_count = len(recipe_details.get('extendedIngredients', []))
    
    if prep_time <= 20 and ingredients_count <= 5:
        return "Easy"
    elif prep_time >= 60 or ingredients_count >= 12:
        return "Hard"
    else:
        return "Medium"

def generate_recipe_details(recipe_data: dict) -> str:
    """Generate a formatted string of recipe details."""
    if not recipe_data:
        return "Recipe details not available"
        
    details = []
    details.append(f"# {recipe_data.get('title', 'Untitled Recipe')}\n")
    
    # Basic info
    details.append(f"🔥 **Calories:** {recipe_data.get('calories', 'Not available')}")
    details.append(f"⏱️ **Time:** {recipe_data.get('readyInMinutes', 'Not specified')} mins")
    details.append(f"💰 **Price:** ${recipe_data.get('pricePerServing', 'N/A')}/serving")
    details.append(f"🥗 **Dietary:** {', '.join(recipe_data.get('diets', ['Not specified']))}")
    details.append(f"🌎 **Cuisine:** {', '.join(recipe_data.get('cuisines', ['Not specified']))}")
    
    # Ingredients
    details.append("\n### 🧂 Ingredients")
    if 'extendedIngredients' in recipe_data:
        for ingredient in recipe_data['extendedIngredients']:
            details.append(f"- {ingredient.get('original', '')}")
    
    # Instructions
    details.append("\n### 📝 Instructions")
    if 'instructions' in recipe_data:
        details.append(recipe_data['instructions'])
    else:
        details.append("Instructions not available")
    
    return "\n".join(details)

# Add this at the very bottom of the file
__all__ = [
    'render_recipe_page',
    'display_recipes',
    'generate_recipe_details'
]