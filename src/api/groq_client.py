import os
import streamlit as st
from groq import Groq

def initialize_groq_client():
    """Initialize and return Groq client."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        # Initialize the client using the current API structure
        client = Groq(api_key=api_key)
        return client
        
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {str(e)}")
        raise

def generate_recipe_details(groq_client, recipe):
    """Generate detailed recipe information using Groq API."""
    try:
        prompt = f"""
        Generate a detailed recipe for "{recipe['title']}" based on the following information:

        Ingredients:
        {' '.join([f"- {ingredient['original']}" for ingredient in recipe.get('usedIngredients', []) + recipe.get('missedIngredients', [])])}

        Provide the following information in this exact format:

        Key Information:
        Calories: [Estimated calories per serving]
        Cooking Time: [Estimated total time in minutes]
        Price: [Estimated price per serving in USD]
        Dietary: [List any dietary categories this recipe fits, e.g., Vegetarian, Vegan, Gluten-Free, etc.]
        Cuisine: [Type of cuisine, e.g., Italian, Mexican, etc.]
        Difficulty: [Easy/Medium/Hard]

        Description:
        [Provide a brief, enticing description of the dish in 2-3 sentences]

        Instructions:
        1. [Step 1]
        2. [Step 2]
        ...

        Additional Information:
        [Flavor Profile, Texture, Nutritional Highlights, Serving Suggestions, Tips]
        """

        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful culinary assistant with expertise in various cuisines and cooking techniques."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating recipe details: {str(e)}")
        return "Recipe details unavailable"