from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import platform

import os
import cv2
from PIL import Image as PILImage
import numpy as np
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import requests
import tempfile

# Load environment variables
load_dotenv()

# Initialize API clients
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class FoodEaseApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.image_widget = Image()
        self.upload_button = Button(text='Upload Image', on_press=self.upload_image)
        self.analyze_button = Button(text='Analyze Fridge', on_press=self.analyze_fridge)
        self.result_label = Label(text='Upload an image to start')

        self.layout.add_widget(self.image_widget)
        self.layout.add_widget(self.upload_button)
        self.layout.add_widget(self.analyze_button)
        self.layout.add_widget(self.result_label)

        return self.layout

    def upload_image(self, instance):
        # For Android, you'd use the Android-specific file chooser
        # This is a placeholder for demonstration
        if platform == 'android':
            from android.storage import primary_external_storage_path
            from android import activity
            from jnius import autoclass

            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            activity.startActivityForResult(intent, 0)

            # You'd then handle the result in the on_activity_result method
        else:
            # For desktop testing
            self.image_path = 'path/to/test/image.jpg'
            self.image_widget.source = self.image_path

    def analyze_fridge(self, instance):
        if hasattr(self, 'image_path'):
            # Placeholder for the actual analysis logic
            # You'd implement the image analysis here using the Google Gemini model
            self.result_label.text = "Analysis complete. Found: apple, milk, cheese"
            # Then you'd call the recipe suggestion function
            self.suggest_recipes(['apple', 'milk', 'cheese'])
        else:
            self.result_label.text = "Please upload an image first"

    def suggest_recipes(self, ingredients):
        # Placeholder for recipe suggestion logic
        # You'd implement the Spoonacular API call here
        self.result_label.text += "\nRecipe suggestions: Apple Pie, Cheese Fondue"

if __name__ == '__main__':
    FoodEaseApp().run()