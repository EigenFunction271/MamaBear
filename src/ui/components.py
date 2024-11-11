import streamlit as st

def create_recipe_card(recipe, recipe_details):
    """Create a styled recipe card using Streamlit components."""
    # First, ensure recipe_details is properly escaped
    recipe_details = recipe_details.replace("<", "&lt;").replace(">", "&gt;")
    
    card_html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; padding:10px; margin:5px 0; background-color:white; box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <img src="{recipe.get('image', '')}" style="width:100%; border-radius:6px; margin-bottom:10px">
        <h3 style="color:#1f1f1f; margin-bottom:10px">{recipe.get('title', 'Recipe Title')}</h3>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px">
            <div>
                <p>🔥 <strong>Calories:</strong> {recipe.get('calories', 'Not available')}</p>
                <p>⏱️ <strong>Time:</strong> {recipe.get('readyInMinutes', 'Not specified')} mins</p>
                <p>💰 <strong>Price:</strong> ${recipe.get('pricePerServing', 'N/A')}/serving</p>
            </div>
            <div>
                <p>🥗 <strong>Dietary:</strong> {recipe.get('diets', ['Not specified'])[0] if recipe.get('diets') else 'Not specified'}</p>
                <p>🌎 <strong>Cuisine:</strong> {recipe.get('cuisines', ['Not specified'])[0] if recipe.get('cuisines') else 'Not specified'}</p>
                <p>📊 <strong>Difficulty:</strong> {recipe.get('difficulty', 'Not specified')}</p>
            </div>
        </div>

        <h4>🧂 Ingredients</h4>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px">
            <div>
                <p><strong>Available:</strong><br>
                {', '.join([ing['name'] for ing in recipe.get('usedIngredients', []) if isinstance(ing, dict) and 'name' in ing]) or 'None'}</p>
            </div>
            <div>
                <p><strong>Missing:</strong><br>
                {', '.join([ing['name'] for ing in recipe.get('missedIngredients', []) if isinstance(ing, dict) and 'name' in ing]) or 'None'}</p>
            </div>
        </div>

        <h4>📝 Instructions</h4>
        <div style="height:200px; overflow-y:auto; padding:8px; border:1px solid #eee; border-radius:4px">
            <p style="white-space:pre-line">{recipe_details}</p>
        </div>
    </div>
    """
    
    return card_html

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