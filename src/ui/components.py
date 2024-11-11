import streamlit as st

def create_recipe_card(recipe, recipe_details):
    """Create a styled recipe card using Streamlit components."""
    # Parse ingredients
    missed_ingredients = ', '.join([
        ing['name'] for ing in recipe.get('missedIngredients', [])
        if isinstance(ing, dict) and 'name' in ing
    ])
    used_ingredients = ', '.join([
        ing['name'] for ing in recipe.get('usedIngredients', [])
        if isinstance(ing, dict) and 'name' in ing
    ])
    
    # Initialize key_info with default values before parsing
    key_info = {
        'Calories': 'Not available',
        'Cooking Time': 'Not specified',
        'Price': 'Not calculated',
        'Dietary': 'Not specified',
        'Cuisine': 'Not specified',
        'Difficulty': 'Not specified'
    }
    
    # Update key_info with parsed values if recipe_details exists
    if recipe_details:
        parsed_info = parse_recipe_key_info(recipe_details)
        key_info.update(parsed_info)
    
    with st.container():
        # Recipe image - using new use_container_width parameter
        if recipe.get('image'):
            st.image(
                recipe.get('image'),
                use_container_width=True  # Updated from use_column_width
            )
        
        # Recipe title
        st.header(recipe.get('title', 'Recipe Title'))
        
        # Recipe info in columns
        col1, col2 = st.columns(2)
        with col1:
            st.write("🔥 **Calories:** ", key_info.get('Calories', 'Not available'))
            st.write("⏱️ **Cooking Time:** ", key_info.get('Cooking Time', 'Not specified'))
            st.write("💰 **Price:** ", key_info.get('Price', 'Not calculated'))
        
        with col2:
            st.write("🥗 **Dietary:** ", key_info.get('Dietary', 'Not specified'))
            st.write("🌎 **Cuisine:** ", key_info.get('Cuisine', 'Not specified'))
            st.write("📊 **Difficulty:** ", key_info.get('Difficulty', 'Not specified'))
        
        # Ingredients section
        st.markdown("---")  # Divider
        st.subheader("🧂 Ingredients")
        
        ingredients_col1, ingredients_col2 = st.columns(2)
        with ingredients_col1:
            st.write("**Available:**")
            st.write(used_ingredients or 'None')
        with ingredients_col2:
            st.write("**Missing:**")
            st.write(missed_ingredients or 'None')
        
        # Instructions
        if recipe_details:
            st.markdown("---")  # Divider
            st.subheader("📝 Instructions")
            st.write(recipe_details)

def parse_recipe_key_info(recipe_details: str) -> dict:
    """Parse key information from recipe details."""
    key_info = {}
    try:
        if isinstance(recipe_details, str) and "Key Information:" in recipe_details:
            key_info_section = recipe_details.split("Key Information:")[1].split("\n\n")[0]
            for line in key_info_section.split("\n"):
                if ":" in line:
                    key, value = [part.strip() for part in line.split(":", 1)]
                    key_info[key] = value
    except Exception as e:
        st.error(f"Error parsing recipe details: {str(e)}")
    return key_info