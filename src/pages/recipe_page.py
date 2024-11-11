import streamlit as st
from src.utils.image_processing import process_image
from src.services.image_analysis_service import analyze_fridge_image
from src.services.recipe_service import get_recipes_from_spoonacular
from src.ui.components import create_recipe_card

def render_recipe_page(apis):
    """Render the recipe analysis and suggestion page."""
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
        with st.spinner("🔍 Processing your image..."):
            temp_path = process_image(uploaded_file)
            if temp_path:
                try:
                    # Analyze image
                    analysis_result, annotated_image, items_info = analyze_fridge_image(temp_path)
                    
                    if analysis_result and items_info:
                        # Store results in session state
                        st.session_state.current_analysis = analysis_result
                        st.session_state.current_annotated_image = annotated_image
                        st.session_state.current_items_info = items_info
                        
                        # Clear previous recipes when new image is uploaded
                        st.session_state.current_recipes = None
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
    """Display recipe cards in a grid layout."""
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
        
        with st.spinner("🔍 Searching for recipes..."):
            recipes = get_recipes_from_spoonacular(ingredients_key)
            st.session_state.current_recipes = recipes
    
    if st.session_state.current_recipes:
        cols = st.columns(2)
        for idx, recipe in enumerate(st.session_state.current_recipes):
            with cols[idx % 2]:
                # Container for each recipe with reduced padding
                with st.container():
                    # Get recipe details
                    recipe_details = generate_recipe_details(groq_client, recipe)
                    
                    # Display recipe image and title with minimal spacing
                    st.image(recipe.get('image', ''), use_container_width=True)
                    st.markdown(f"### {recipe['title']}")
                    
                    # Basic info in compact columns
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.markdown("🔥 **Calories:** " + str(recipe.get('calories', 'Not available')))
                        st.markdown("⏱️ **Time:** " + str(recipe.get('readyInMinutes', 'Not specified')) + " mins")
                        st.markdown("💰 **Price:** $" + str(recipe.get('pricePerServing', 'N/A')) + "/serving")
                    
                    with info_col2:
                        st.markdown("🥗 **Dietary:** " + (recipe.get('diets', ['Not specified'])[0] if recipe.get('diets') else 'Not specified'))
                        st.markdown("🌎 **Cuisine:** " + (recipe.get('cuisines', ['Not specified'])[0] if recipe.get('cuisines') else 'Not specified'))
                        st.markdown("📊 **Difficulty:** " + str(recipe.get('difficulty', 'Not specified')))
                    
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
                        st.markdown(recipe_details)
                    
                    # Schedule button
                    st.button(f"📅 Schedule {recipe['title']}", key=f"schedule_{idx}")
                    
                    # Add a small divider between recipes
                    st.markdown("---")
    else:
        st.warning("No recipes found. Try with different ingredients.")

def generate_recipe_details(groq_client, recipe):
    """Generate detailed recipe information using Groq."""
    try:
        prompt = f"""
        Generate a detailed recipe for "{recipe['title']}" with:
        - Estimated cooking time
        - Difficulty level
        - Servings
        - Key steps
        
        Format the response as plain text without any HTML or CSS elements.
        """
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant. Provide recipe details in plain text format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Clean the response to ensure it's plain text
        recipe_text = response.choices[0].message.content
        # Remove any HTML-like tags that might be in the response
        recipe_text = recipe_text.replace("<", "&lt;").replace(">", "&gt;")
        return recipe_text
    except Exception as e:
        st.error(f"Error generating recipe details: {str(e)}")
        return "Recipe details unavailable"