from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import streamlit as st
from src.utils.streamlit_context import with_streamlit_context
import logging
import pytz

logger = logging.getLogger(__name__)

class MealPlannerService:
    def __init__(self):
        try:
            self.SCOPES = ['https://www.googleapis.com/auth/calendar']
            self.credentials = self._get_credentials()
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Successfully initialized MealPlannerService")
        except Exception as e:
            logger.error(f"Failed to initialize MealPlannerService: {str(e)}")
            raise

    def _get_credentials(self) -> Credentials:
        """Get or refresh Google Calendar credentials."""
        creds = None
        
        # Check if credentials are stored in Streamlit session state
        if 'google_creds' in st.session_state:
            creds = st.session_state.google_creds
            
        # If no valid credentials available, let the user authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {str(e)}")
                    creds = None
            
            if not creds:
                try:
                    # Load client configuration from environment or secrets
                    client_config = {
                        "installed": {
                            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    }
                    
                    flow = InstalledAppFlow.from_client_config(
                        client_config,
                        self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    
                    # Save credentials in session state
                    st.session_state.google_creds = creds
                    
                except Exception as e:
                    logger.error(f"Failed to authenticate: {str(e)}")
                    raise ValueError("Failed to authenticate with Google Calendar. Please check your credentials.")
        
        return creds

    @with_streamlit_context
    def find_meal_prep_slots(
        self, 
        recipe: Dict, 
        days_ahead: int = 7
    ) -> List[Dict]:
        """Find available time slots for meal preparation."""
        try:
            cooking_time = recipe.get('readyInMinutes', 30)
            
            # Add buffer time to now to ensure slots start in the future
            now = datetime.now(pytz.UTC) + timedelta(minutes=5)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} calendar events")

            # Process events and find available slots
            available_slots = []

            # Create slots for each day based on recipe cooking time
            for day in range(days_ahead):
                day_start = (now + timedelta(days=day)).replace(
                    hour=6,  # Start at 6 AM
                    minute=0,
                    second=0,
                    microsecond=0
                )
                day_end = day_start.replace(hour=22)  # End at 10 PM
                
                # Start from the first valid time for today
                current_slot_start = max(day_start, now)
                
                # Create slots matching recipe cooking time
                while current_slot_start + timedelta(minutes=cooking_time) <= day_end:
                    slot_end = current_slot_start + timedelta(minutes=cooking_time)
                    
                    # Check if slot overlaps with any events
                    overlaps = False
                    if events:
                        for event in events:
                            event_start = datetime.fromisoformat(
                                event['start'].get('dateTime', event['start'].get('date'))
                            ).astimezone(pytz.UTC)
                            event_end = datetime.fromisoformat(
                                event['end'].get('dateTime', event['end'].get('date'))
                            ).astimezone(pytz.UTC)
                            
                            if (current_slot_start < event_end and slot_end > event_start):
                                overlaps = True
                                break
                    
                    if not overlaps:
                        local_start = current_slot_start.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))
                        available_slots.append({
                            'start': current_slot_start.isoformat(),
                            'end': slot_end.isoformat(),
                            'duration_minutes': cooking_time,
                            'day': local_start.strftime('%A, %B %d'),
                            'display_time': f"{local_start.strftime('%I:%M %p')} - {local_start + timedelta(minutes=cooking_time):%I:%M %p}"
                        })
                    
                    # Move to next slot with a 5-minute buffer
                    current_slot_start = current_slot_start + timedelta(minutes=cooking_time + 5)

            # Filter out slots that are too close to now
            available_slots = [
                slot for slot in available_slots 
                if datetime.fromisoformat(slot['start']) > now
            ]

            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots

        except Exception as e:
            logger.error(f"Error finding meal prep slots: {str(e)}")
            return []

    @with_streamlit_context
    def schedule_meal_prep(
        self, 
        recipe: Dict,
        start_time: datetime,
        meal_type: str = "Meal"
    ) -> bool:
        """Schedule a meal preparation session."""
        try:
            recipe_name = recipe.get('title', 'Unknown Recipe')
            duration_minutes = recipe.get('readyInMinutes', 30)
            
            # Ensure timezone-aware datetime for both now and start_time
            now = datetime.now(pytz.UTC)
            
            # Convert start_time to UTC if it's naive
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            else:
                start_time = start_time.astimezone(pytz.UTC)
            
            # Add a small buffer (e.g., 1 minute) to avoid immediate future conflicts
            if start_time <= now + timedelta(minutes=1):
                logger.error(f"Selected time {start_time} is too close to current time {now}")
                raise ValueError("Please select a time at least 1 minute in the future")

            event = {
                'summary': f'{meal_type} Prep: {recipe_name}',
                'description': f'Preparing {recipe_name}\nEstimated time: {duration_minutes} minutes',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (start_time + timedelta(minutes=duration_minutes)).isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': True
                },
            }

            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Successfully scheduled meal prep: {created_event.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error scheduling meal prep: {str(e)}")
            return False

def initialize_meal_planner() -> MealPlannerService:
    """Initialize and return MealPlannerService."""
    try:
        return MealPlannerService()
    except Exception as e:
        st.error(f"Failed to initialize MealPlannerService: {str(e)}")
        raise