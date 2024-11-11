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
    # Use cached recipes if available, otherwise fetch new ones
    if st.session_state.current_recipes is None:
        ingredients_key = tuple(sorted(items_info.keys()))
        
        with st.spinner("🔍 Searching for recipes..."):
            recipes = get_recipes_from_spoonacular(ingredients_key)
            st.session_state.current_recipes = recipes
    
    if st.session_state.current_recipes:
        # Display recipes in grid
        cols = st.columns(2)
        for idx, recipe in enumerate(st.session_state.current_recipes):
            with cols[idx % 2]:
                recipe_details = generate_recipe_details(groq_client, recipe)
                st.markdown(create_recipe_card(recipe, recipe_details), unsafe_allow_html=True)
                
                # Add scheduling button for each recipe
                if st.button(f"📅 Schedule {recipe['title']}", key=f"schedule_{idx}"):
                    st.session_state.selected_recipe = recipe
                    st.session_state.page = "Meal Planning"
    else:
        st.warning("No recipes found. Try with different ingredients.")

def generate_recipe_details(groq_client, recipe):
    """Generate detailed recipe information using Groq."""
    try:
        prompt = f"""
        Generate a detailed recipe for "{recipe['title']}" with:
        - Estimated cooking time
        - Difficulty level
        - Key steps
        """
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating recipe details: {str(e)}")
        return "Recipe details unavailable"