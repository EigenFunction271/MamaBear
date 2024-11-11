import streamlit as st
from datetime import datetime, timedelta
import pytz
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from src.services.meal_planner_service import initialize_meal_planner
from typing import Dict, List, Optional

def create_calendar_view(events, selected_slot=None):
    """Create a Gantt chart calendar view using plotly."""
    if not events:
        return None
        
    # Prepare data for Gantt chart
    df_dict = {
        'Task': [],
        'Start': [],
        'Finish': [],
        'Type': []  # To differentiate between existing events and selected slot
    }
    
    # Add existing events
    for event in events:
        start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))).replace(tzinfo=pytz.UTC)
        end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date'))).replace(tzinfo=pytz.UTC)
        
        df_dict['Task'].append(event.get('summary', 'Busy'))
        df_dict['Start'].append(start)
        df_dict['Finish'].append(end)
        df_dict['Type'].append('existing')
    
    # Add selected slot if exists
    if selected_slot:
        start = datetime.fromisoformat(selected_slot['start'])
        end = datetime.fromisoformat(selected_slot['end'])
        df_dict['Task'].append('Selected Meal Prep')
        df_dict['Start'].append(start)
        df_dict['Finish'].append(end)
        df_dict['Type'].append('selected')
    
    df = pd.DataFrame(df_dict)
    
    # Create color mapping
    colors = {
        'existing': 'rgb(100, 149, 237)',  # Cornflower blue
        'selected': 'rgb(255, 127, 80)'    # Coral
    }
    
    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Type',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True
    )
    
    # Update layout
    fig.update_layout(
        title='Calendar View',
        height=400,
        xaxis_title='Date/Time',
        yaxis_title='Events'
    )
    
    return fig

def render_meal_planner_page(recipe_data=None):
    st.header("📅 Meal Planning")
    
    if not recipe_data:
        st.warning("Please select a recipe first!")
        return

    try:
        meal_planner = initialize_meal_planner()
        
        # Display recipe details
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"Planning for: {recipe_data['title']}")
            st.write(f"Preparation time: {recipe_data.get('readyInMinutes', 30)} minutes")
        
        with col2:
            planning_window = st.selectbox(
                "Planning Window",
                options=[7, 14, 21],
                format_func=lambda x: f"{x} days",
                help="How far ahead would you like to plan?",
                index=0
            )

        # Get calendar events for display
        now = datetime.now(pytz.UTC)
        time_max = (now + timedelta(days=planning_window)).isoformat()
        
        events_result = meal_planner.service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Display current calendar
        st.subheader("Current Schedule")
        calendar_fig = create_calendar_view(events)
        if calendar_fig:
            st.plotly_chart(calendar_fig, use_container_width=True)
        else:
            st.info("No events scheduled in the selected time period.")

        # Find available time slots
        with st.spinner("Finding available time slots..."):
            available_slots = meal_planner.find_meal_prep_slots(
                recipe_data,
                days_ahead=planning_window
            )

        if not available_slots:
            st.warning(f"No available time slots found in the next {planning_window} days.")
            return

        # Group and display available slots
        st.subheader("Available Time Slots")
        slots_by_date = {}
        selected_slot = None
        
        for slot in available_slots:
            start_time = datetime.fromisoformat(slot['start'])
            date_key = start_time.strftime('%Y-%m-%d')
            if date_key not in slots_by_date:
                slots_by_date[date_key] = []
            slots_by_date[date_key].append(slot)

        for date_key, slots in slots_by_date.items():
            date_obj = datetime.strptime(date_key, '%Y-%m-%d')
            st.write(f"**{date_obj.strftime('%A, %B %d')}**")
            
            cols = st.columns(2)
            for i, slot in enumerate(slots):
                start_time = datetime.fromisoformat(slot['start'])
                end_time = datetime.fromisoformat(slot['end'])
                
                with cols[i % 2]:
                    slot_text = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} UTC"
                    if st.button(f"📅 {slot_text}", key=f"slot_{date_key}_{i}"):
                        selected_slot = slot
                        
                        # Update calendar view with selected slot
                        updated_fig = create_calendar_view(events, selected_slot)
                        if updated_fig:
                            st.plotly_chart(updated_fig, use_container_width=True)

        # Schedule the selected slot
        if selected_slot:
            with st.spinner("Scheduling meal prep..."):
                start_time = datetime.fromisoformat(selected_slot['start'])
                success = meal_planner.schedule_meal_prep(
                    recipe=recipe_data,
                    start_time=start_time
                )
                
                if success:
                    st.success("Meal prep scheduled successfully! Check your Google Calendar.")
                else:
                    st.error("Failed to schedule meal prep. Please try again.")

    except Exception as e:
        st.error(f"Error in meal planner: {str(e)}")