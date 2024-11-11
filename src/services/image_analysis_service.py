import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import logging
import json
from typing import Dict, Any
from functools import wraps
import time
import threading

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def timeout(seconds):
    """Timeout decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import threading
            result = []
            def target():
                result.append(func(*args, **kwargs))
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(seconds)
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            return result[0]
        return wrapper
    return decorator

def with_streamlit_context(func):
    """Decorator to handle Streamlit's threading context."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

def initialize_gemini():
    """Initialize Google Gemini AI."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
            
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)
        
        try:
            # Use Gemini 1.5 Pro model
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Test the model with a simple request
            logger.info("Testing Gemini model connection...")
            response = model.generate_content(["Hello"])
            if not response:
                raise ValueError("Could not validate model connection")
                
        except Exception as e:
            logger.error(f"Error testing model: {str(e)}")
            raise ValueError(f"Failed to initialize model: {str(e)}")
            
        logger.info("Successfully initialized Gemini AI")
        return model
        
    except Exception as e:
        error_msg = f"Failed to initialize Gemini AI: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        raise

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    if not hex_color:
        return (0, 0, 0)  # Default to black if no color provided
    
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_annotations(image: Image, items_info: Dict, analysis_result: str) -> Image:
    """Draw bounding boxes and labels on the image."""
    try:
        # Create a copy of the image for annotations
        annotated = image.copy()
        width, height = annotated.size
        
        # Create a transparent overlay for the boxes
        overlay = Image.new('RGBA', annotated.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Load a font for labels
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            
        # Define colors for different categories
        colors = {
            'dairy': (255, 182, 193, 160),    # Light pink
            'meat': (250, 128, 114, 160),     # Salmon
            'fruit': (152, 251, 152, 160),    # Pale green
            'vegetable': (144, 238, 144, 160), # Light green
            'condiment': (255, 218, 185, 160), # Peach
            'other': (176, 196, 222, 160)      # Light steel blue
        }
        
        # Draw boxes and labels
        for item_name, info in items_info.items():
            if 'box' in info:
                # Get normalized coordinates
                box = info['box']
                
                # Ensure coordinates are valid
                x0, y0 = min(box[0], box[2]), min(box[1], box[3])
                x1, y1 = max(box[0], box[2]), max(box[1], box[3])
                
                # Get color based on category
                color = colors.get(info.get('category', 'other'), colors['other'])
                
                # Draw semi-transparent box
                draw.rectangle([x0, y0, x1, y1], fill=color)
                
                # Draw label
                label = f"{item_name}: {info.get('quantity', 'unknown')}"
                draw.text((x0, y0-15), label, font=font, fill=(0, 0, 0, 255))
        
        # Combine the original image with the overlay
        annotated = Image.alpha_composite(annotated.convert('RGBA'), overlay)
        return annotated.convert('RGB')
        
    except Exception as e:
        logger.error(f"Error creating annotations: {str(e)}")
        return image

def extract_organization_suggestions(analysis: str) -> list:
    """Extract organization suggestions from the analysis text."""
    suggestions = []
    
    # Look for organization-related sentences
    lines = analysis.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['should be', 'could be', 'move', 'organize', 'arrange']):
            suggestions.append({
                'text': line.strip(),
                'location': 'center'  # Default location
            })
    
    return suggestions[:5]  # Limit to 5 suggestions to avoid cluttering

def parse_location(location: str, width: int, height: int) -> tuple:
    """Convert location description to x,y coordinates."""
    # Simple mapping of common locations to coordinates
    locations = {
        'top': (width//2, height//4),
        'bottom': (width//2, 3*height//4),
        'left': (width//4, height//2),
        'right': (3*width//4, height//2),
        'center': (width//2, height//2),
        'top_left': (width//4, height//4),
        'top_right': (3*width//4, height//4),
        'bottom_left': (width//4, 3*height//4),
        'bottom_right': (3*width//4, 3*height//4)
    }
    return locations.get(location.lower().replace(' ', '_'), (width//2, height//2))

def analyze_with_timeout(model, prompt, image, timeout_seconds=45):
    """Helper function to run Gemini analysis with timeout."""
    start_time = time.time()
    
    def run_analysis():
        try:
            # Remove timeout parameter and just call generate_content
            response = model.generate_content([prompt, image])
            if not response:
                raise ValueError("Empty response from Gemini")
            return response
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Gemini API error: {str(e)}")
            raise

    try:
        # Create and start thread
        result = []
        thread = threading.Thread(target=lambda: result.append(run_analysis()))
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            logger.error(f"[{time.time() - start_time:.2f}s] Analysis timed out after {timeout_seconds} seconds")
            raise TimeoutError(f"Analysis timed out after {timeout_seconds} seconds")
            
        if not result:
            raise Exception("No result generated")
            
        return result[0]
        
    except TimeoutError:
        # Try one more time with a longer timeout
        logger.warning(f"[{time.time() - start_time:.2f}s] Retrying analysis with extended timeout")
        thread = threading.Thread(target=lambda: result.append(run_analysis()))
        thread.start()
        thread.join(timeout_seconds + 30)  # Add 30 seconds for retry
        
        if thread.is_alive() or not result:
            raise TimeoutError(f"Analysis timed out after {timeout_seconds + 30} seconds")
            
        return result[0]

@timeout(90)  # Increase overall timeout to 90 seconds
@with_streamlit_context
def analyze_fridge_image(image_path):
    """Analyze fridge image using Gemini Pro Vision."""
    start_time = time.time()
    
    try:
        logger.info(f"[{time.time() - start_time:.2f}s] Starting image analysis for: {image_path}")
        
        # Add status indicator with more detailed progress
        status = st.empty()
        progress = st.progress(0)
        status.info("Initializing Gemini AI...")
        
        # Initialize Gemini
        try:
            model = initialize_gemini()
            logger.info(f"[{time.time() - start_time:.2f}s] Gemini initialization complete")
            progress.progress(10)
        except Exception as e:
            logger.error(f"Gemini initialization failed after {time.time() - start_time:.2f}s: {str(e)}")
            raise
            
        # Open and process image
        try:
            image = Image.open(image_path)
            width, height = image.size
            logger.info(f"[{time.time() - start_time:.2f}s] Image loaded: {image.size}, mode: {image.mode}")
            progress.progress(20)
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Failed to load image: {str(e)}")
            raise
            
        status.info("Analyzing image contents...")
        
        # Generate object detection using Gemini
        logger.info(f"[{time.time() - start_time:.2f}s] Starting object detection")
        try:
            detection_prompt = """
            Analyze this refrigerator image and provide a JSON response with the following structure:
            {
                "items": {
                    "item_name": {
                        "quantity": "number or approximate amount",
                        "category": "fruit/vegetable/dairy/beverage/condiment/meat/other",
                        "box": [x1, y1, x2, y2],  // Coordinates in percentage of image size (0-100)
                        "freshness": "fresh/good/check/expired"  // Optional freshness status
                    }
                }
            }
            """
            
            detection_response = analyze_with_timeout(model, detection_prompt, image, timeout_seconds=45)
            logger.info(f"[{time.time() - start_time:.2f}s] Object detection complete")
            progress.progress(50)
            
        except TimeoutError as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Object detection timed out: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Object detection failed: {str(e)}")
            raise
            
        # Process detection response
        try:
            json_str = detection_response.text.strip()
            logger.debug(f"[{time.time() - start_time:.2f}s] Raw detection response: {json_str}")
            
            # Extract JSON content
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            items_info = json.loads(json_str)["items"]
            logger.info(f"[{time.time() - start_time:.2f}s] Successfully parsed items_info with {len(items_info)} items")
            
            # Convert coordinates
            for item in items_info.values():
                if 'box' in item:
                    box = item['box']
                    item['box'] = [
                        int(box[0] * width / 100),
                        int(box[1] * height / 100),
                        int(box[2] * width / 100),
                        int(box[3] * height / 100)
                    ]
                    
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Error parsing detection response: {str(e)}")
            items_info = {}

        # Generate detailed analysis
        logger.info(f"[{time.time() - start_time:.2f}s] Starting detailed analysis")
        try:
            analysis_prompt = """
            Analyze this refrigerator image in detail. Please provide:
            1. A list of all visible items and their approximate quantities
            2. The organization and storage of items
            3. The freshness status of visible perishable items
            4. Any notable missing basic items
            5. Suggestions for what could be cooked with these ingredients
            6. Specific tips for better organization, including where items should be moved
            """
            
            analysis_response = analyze_with_timeout(model, analysis_prompt, image, timeout_seconds=45)
            logger.info(f"[{time.time() - start_time:.2f}s] Detailed analysis complete")
            
            if not analysis_response or not analysis_response.text:
                raise ValueError("No analysis generated")
                
            analysis_result = analysis_response.text
            
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Detailed analysis failed: {str(e)}")
            raise

        # Create annotated image
        logger.info(f"[{time.time() - start_time:.2f}s] Creating annotated image")
        try:
            annotated_image = image.convert('RGB')
            if items_info:
                annotated_image = draw_annotations(annotated_image, items_info, analysis_result)
            logger.info(f"[{time.time() - start_time:.2f}s] Annotation complete")
        except Exception as e:
            logger.error(f"[{time.time() - start_time:.2f}s] Failed to create annotations: {str(e)}")
            raise

        total_time = time.time() - start_time
        logger.info(f"[{total_time:.2f}s] Analysis completed successfully")
        progress.progress(100)
        return analysis_result, annotated_image, items_info

    except TimeoutError as e:
        elapsed = time.time() - start_time
        logger.error(f"Analysis timed out after {elapsed:.2f}s: {str(e)}")
        st.error("Analysis took too long. Please try again.")
        return None, None, None
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error analyzing image after {elapsed:.2f}s: {str(e)}", exc_info=True)
        st.error("Could not analyze the image. Please try again.")
        return None, None, None
def parse_detection_response(response_text: str) -> dict:
    """Parse the detection response, cleaning any JSON formatting issues."""
    try:
        # Remove trailing comma before closing brace
        cleaned_json = response_text.replace(",\n  }", "\n  }")
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        logger.error(f"[{time.time()}s] Error parsing detection response: {str(e)}")
        # Return empty dict as fallback
        return {"items": {}}
