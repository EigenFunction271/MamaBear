from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import streamlit as st

class MealPlannerService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials = self._get_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        """Get or refresh Google Calendar credentials."""
        creds = None
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    def find_meal_prep_slots(
        self, 
        recipe: Dict, 
        days_ahead: int = 7,
        min_slot_duration: int = 30  # minutes
    ) -> List[Dict]:
        """
        Find available time slots for meal preparation.
        
        Args:
            recipe: Recipe dictionary containing cooking time
            days_ahead: Number of days to look ahead
            min_slot_duration: Minimum duration needed for meal prep
            
        Returns:
            List of available time slots
        """
        try:
            # Calculate time boundaries
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

            # Get busy periods from calendar
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            # Find free slots
            available_slots = []
            current_time = now

            for event in events:
                start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                
                # Check if there's enough time before the event
                gap_duration = (start - current_time).total_seconds() / 60
                if gap_duration >= min_slot_duration:
                    available_slots.append({
                        'start': current_time.isoformat(),
                        'end': start.isoformat(),
                        'duration_minutes': gap_duration
                    })
                
                current_time = end

            return available_slots

        except Exception as e:
            st.error(f"Error finding meal prep slots: {str(e)}")
            return []

    def schedule_meal_prep(
        self, 
        recipe_name: str,
        start_time: datetime,
        duration_minutes: int
    ) -> bool:
        """
        Schedule a meal preparation session in Google Calendar.
        
        Args:
            recipe_name: Name of the recipe
            start_time: Start time for meal prep
            duration_minutes: Expected duration of meal prep
            
        Returns:
            Boolean indicating success
        """
        try:
            event = {
                'summary': f'Meal Prep: {recipe_name}',
                'description': f'Preparing {recipe_name}',
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

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return True

        except Exception as e:
            st.error(f"Error scheduling meal prep: {str(e)}")
            return False

def initialize_meal_planner() -> MealPlannerService:
    """Initialize and return MealPlannerService."""
    try:
        return MealPlannerService()
    except Exception as e:
        st.error(f"Failed to initialize MealPlannerService: {str(e)}")
        raise