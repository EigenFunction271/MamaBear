import os
import cv2
import numpy as np
from google.cloud import vision
import google.generativeai as genai
import streamlit as st
from PIL import Image, ImageDraw
from src.utils.decorators import timeout

def initialize_vision_client():
    """Initialize Google Cloud Vision client."""
    try:
        return vision.ImageAnnotatorClient()
    except Exception as e:
        st.error(f"Failed to initialize Vision API: {str(e)}")
        raise

def initialize_gemini():
    """Initialize Google Gemini AI."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai.GenerativeModel('gemini-pro-vision')
    except Exception as e:
        st.error(f"Failed to initialize Gemini AI: {str(e)}")
        raise

@timeout(60)
def analyze_fridge_image(image_path):
    """Analyze fridge image using Google Cloud Vision and Gemini AI."""
    try:
        # Initialize clients
        vision_client = initialize_vision_client()
        gemini_model = initialize_gemini()
        
        # Read image for Vision API
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Perform object detection
        image = vision.Image(content=content)
        objects = vision_client.object_localization(image=image).localized_object_annotations
        
        # Process detected objects
        detected_items = {}
        annotated_image = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(annotated_image)
        
        for obj in objects:
            name = obj.name.lower()
            if name not in detected_items:
                detected_items[name] = 1
            else:
                detected_items[name] += 1
            
            # Draw bounding box
            vertices = [(vertex.x * annotated_image.width, vertex.y * annotated_image.height)
                       for vertex in obj.bounding_poly.normalized_vertices]
            draw.polygon(vertices, outline='red', width=2)
            
            # Add label
            draw.text((vertices[0][0], vertices[0][1] - 10),
                     f"{obj.name} ({obj.score:.2f})",
                     fill='red')
        
        # Generate analysis using Gemini
        analysis_prompt = f"""
        Analyze these items found in a fridge: {', '.join(detected_items.keys())}
        
        Please provide:
        1. A brief summary of the contents
        2. The freshness status of perishable items
        3. Any notable missing basic items
        4. Suggestions for what could be cooked with these ingredients
        """
        
        response = gemini_model.generate_content([analysis_prompt])
        analysis_result = response.text if response else "No analysis available"
        
        return analysis_result, annotated_image, detected_items

    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None, None, None