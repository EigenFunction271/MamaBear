import cv2
from PIL import Image
import tempfile
import streamlit as st
import os

def process_image(uploaded_file, max_size=(800, 800)):
    """Process and resize uploaded image."""
    try:
        image = Image.open(uploaded_file)
        
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_file.name, 'JPEG', quality=85)
        return temp_file.name
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None
    finally:
        if 'image' in locals():
            image.close()