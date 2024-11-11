# MamaBear: AI Family Hub

An AI-powered kitchen assistant that analyzes your fridge contents and suggests recipes using multiple AI models for accurate food detection and personalized recipe recommendations.

## Prerequisites

- Python 3.8 or higher
- Internet connection
- Webcam or food images for analysis
- Required API Keys:
  - Google API Key (for Gemini Vision)
  - Groq API Key (for LLM processing)
  - Spoonacular API Key (for recipe database)

## Environment Setup

1. **Create Environment File**
   - Copy `.env.template` to create your `.env` file:
   ```bash
   cp .env.template .env
   ```
   - Edit `.env` and add your API keys:
     - Required Keys:
       - `GOOGLE_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
       - `GROQ_API_KEY`: Get from [Groq Cloud](https://console.groq.com/)
       - `SPOONACULAR_API_KEY`: Get from [Spoonacular](https://spoonacular.com/food-api)
     - Optional Keys:
       - `OPENAI_API_KEY`: For fallback recipe generation
       - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: For calendar integration

2. **API Setup Instructions**

   ### Google AI (Gemini) Setup:
   1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   2. Create or select a project
   3. Enable the Gemini API
   4. Create an API key
   5. Copy the key to your `.env` file

   ### Groq Setup:
   1. Sign up at [Groq Cloud](https://console.groq.com/)
   2. Navigate to API Keys section
   3. Generate a new API key
   4. Copy the key to your `.env` file

   ### Spoonacular Setup:
   1. Create account at [Spoonacular](https://spoonacular.com/food-api)
   2. Subscribe to a plan (free tier available)
   3. Get your API key from the dashboard
   4. Copy the key to your `.env` file

   ### Google Calendar Setup (Optional):
   1. Visit [Google Cloud Console](https://console.cloud.google.com/)
   2. Create a new project
   3. Enable the Google Calendar API
   4. Configure OAuth consent screen
   5. Create OAuth 2.0 credentials
   6. Copy Client ID and Secret to your `.env` file

## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/foodease.git
cd foodease
```

2. **Set up Python virtual environment**

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

For Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## Running the Application

### Windows Users
Option 1: Double click `run.bat`

Option 2: Open command prompt in project directory and type:
```bash
.\run.bat
```

### Mac/Linux Users
Option 1: Open terminal in project directory and type:
```bash
chmod +x run.sh  # Make script executable (first time only)
./run.sh
```

Option 2: Manual setup:
```bash
# Activate virtual environment
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run application
streamlit run main.py
```

## Features

- 📸 Multi-model AI-powered food detection
  - Gemini Vision for initial image analysis
  - Groq LLM for enhanced ingredient recognition
  - Spoonacular API for recipe matching
- 🔍 Intelligent ingredient categorization and storage
- 🍳 Smart recipe suggestions based on:
  - Available ingredients
  - Dietary preferences
  - Cooking time
- 📊 Interactive web interface powered by Streamlit
- 💾 Session state management for continuous interaction
- 🔄 Real-time image processing and analysis
- 📝 Detailed recipe instructions and ingredient lists

## Technical Requirements

Core Dependencies:
- Python 3.8+
- Streamlit
- OpenCV
- PIL (Pillow)
- python-dotenv

API Integrations:
- Google Generative AI (Gemini Vision API)
- Groq API
- Spoonacular API

See `requirements.txt` for complete list of dependencies.

## Troubleshooting

If you encounter any errors:

1. API Related Issues:
   - Verify all API keys are correctly set in `.env`
   - Check API usage limits and quotas
   - Ensure proper API permissions are enabled

2. Environment Issues:
   - Verify Python version: `python --version`
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` to update dependencies

3. Runtime Issues:
   - Check webcam permissions if using live capture
   - Verify image format compatibility
   - Try running with administrator/sudo privileges

4. Performance Issues:
   - Check internet connection stability
   - Ensure sufficient system resources
   - Consider reducing image size if processing is slow

## Support

For technical support:
1. Check the [Issues](https://github.com/yourusername/foodease/issues) section
2. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - System information
   - Error messages/logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Generative AI team for Gemini Vision API
- Groq team for their LLM API
- Spoonacular team for their comprehensive recipe API
- The Streamlit team for their excellent web framework

