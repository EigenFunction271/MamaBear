import os
from typing import Optional, Tuple
import google.generativeai as genai
import streamlit as st
from PIL import Image
from src.utils.decorators import timeout

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        self.text_model = genai.GenerativeModel('gemini-pro')

    @timeout(30)
    def analyze_image(
        self, 
        image: Image.Image, 
        detected_items: dict
    ) -> Tuple[Optional[str], Optional[dict]]:
        """
        Analyze image and detected items using Gemini AI.
        
        Args:
            image: PIL Image object
            detected_items: Dictionary of detected items and their counts
            
        Returns:
            Tuple of (analysis_text, processed_items)
        """
        try:
            # Prepare the prompt
            prompt = f"""
            Analyze these items found in a fridge: {', '.join(detected_items.keys())}
            
            Please provide:
            1. A brief summary of the contents
            2. The freshness status of perishable items
            3. Any notable missing basic items
            4. Suggestions for what could be cooked with these ingredients
            
            Format the response in clear sections with emoji indicators.
            """

            response = self.model.generate_content([prompt, image])
            
            if response and response.text:
                return response.text, detected_items
            return None, None

        except Exception as e:
            st.error(f"Gemini AI error: {str(e)}")
            return None, None

    @timeout(30)
    def generate_recipe_suggestions(
        self, 
        ingredients: list
    ) -> Optional[str]:
        """
        Generate recipe suggestions based on ingredients.
        
        Args:
            ingredients: List of available ingredients
            
        Returns:
            Generated recipe suggestions or None if error
        """
        try:
            prompt = f"""
            Given these ingredients: {', '.join(ingredients)}
            
            Suggest 3 possible recipes that could be made, including:
            1. Recipe name
            2. Brief description
            3. Additional ingredients needed
            4. Basic preparation steps
            
            Keep it concise but informative.
            """

            response = self.text_model.generate_content(prompt)
            return response.text if response else None

        except Exception as e:
            st.error(f"Error generating recipe suggestions: {str(e)}")
            return None

def initialize_gemini_client() -> GeminiClient:
    """Initialize and return Gemini client."""
    try:
        return GeminiClient()
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {str(e)}")
        raise