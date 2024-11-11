import streamlit as st

def render_home_page():
    """Render the home page with welcome message and instructions."""
    st.markdown("""
    # 🏠 Welcome to MamaBear
    
    Your AI-powered kitchen assistant that helps you:
    - 📸 Analyze fridge contents
    - 🥗 Find recipes with available ingredients
    - 📅 Plan meals around your schedule
    
    ### Getting Started
    1. Use the sidebar to navigate between features
    2. Start by uploading a photo of your fridge
    3. Let AI analyze your ingredients
    4. Browse recipe suggestions
    5. Schedule meal prep times
    
    ### Features
    - **Smart Fridge Analysis**: AI-powered detection of food items
    - **Recipe Matching**: Find recipes using your available ingredients
    - **Meal Planning**: Integrate with your Google Calendar
    
    ### Need Help?
    - Check our [documentation](https://github.com/yourusername/foodease)
    - Report issues on [GitHub](https://github.com/yourusername/foodease/issues)
    """)

    # Optional: Add quick action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Start Analyzing"):
            st.session_state.page = "Recipe Analysis"
    with col2:
        if st.button("📅 Plan Meals"):
            st.session_state.page = "Meal Planning"