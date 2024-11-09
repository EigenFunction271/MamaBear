import streamlit as st

def create_recipe_card(recipe, recipe_details):
    """Create a styled recipe card with HTML/CSS formatting."""
    missed_ingredients = ', '.join([ing['name'] for ing in recipe.get('missedIngredients', [])])
    used_ingredients = ', '.join([ing['name'] for ing in recipe.get('usedIngredients', [])])
    key_info = parse_recipe_key_info(recipe_details)

    for field in ['Calories', 'Cooking Time', 'Price', 'Dietary', 'Cuisine', 'Difficulty']:
        key_info.setdefault(field, "Not Found")

    card_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 600px; overflow-y: auto;">
        <img src="{recipe['image']}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;">
        <h3 style="margin-top: 10px;">{recipe['title']}</h3>
        <p>🔥 **Calories**: {key_info['Calories']}</p>
        <p>⏱️ **Cooking Time**: {key_info['Cooking Time']}</p>
        <p>💰 **Price**: {key_info['Price']}</p>
        <p>🥗 **Dietary**: {key_info['Dietary']}</p>
        <p>🌎 **Cuisine**: {key_info['Cuisine']}</p>
        <p>📊 **Difficulty**: {key_info['Difficulty']}</p>
        <p><strong>Used ingredients:</strong> {used_ingredients}</p>
        <p><strong>Missing ingredients:</strong> {missed_ingredients}</p>
        <div>
            {recipe_details}
        </div>
    </div>
    """
    return card_html

def parse_recipe_key_info(recipe_details):
    """Parse key information from recipe details."""
    key_info = {}
    try:
        key_info_section = recipe_details.split("Key Information:")[1].split("\n\n")[0]
        for line in key_info_section.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key_info[key.strip()] = value.strip()
    except Exception:
        pass
    return key_info