# database.py (COMPLETELY REWRITTEN FOR SUPABASE)
import streamlit as st
import pandas as pd
# Import the connection manager for Supabase
from streamlit_supabase_connection import SupabaseConnection

# Initialize the Supabase Connection (it will look for credentials in .streamlit/secrets.toml)
@st.cache_resource
def get_supabase_connection():
    # Use the connection component name you want (e.g., 'supabase_db')
    return st.experimental_connection("supabase_db", type=SupabaseConnection)

# Global connection object
conn = get_supabase_connection()

# --- Core Database Functions ---

def init_db():
    # Supabase is persistent, so we don't need to create tables.
    # This function remains for consistency but does nothing.
    st.info("Database initialization skipped. Using persistent Supabase tables.")
    pass

@st.cache_data(ttl=60) # Cache the data for 60 seconds to reduce Supabase reads
def get_data(table_name):
    """Fetches all data from the specified table."""
    try:
        # Use st.connection's read method
        df = conn.read(table_name)
        return df
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

# This function is used to populate the filters (Children, Disciplines)
@st.cache_data
def get_list_data(list_type):
    """Fetches list-like data (e.g., child names, disciplines)."""
    if list_type == "disciplines":
        # In this simple example, we are hardcoding the list since you don't have a separate list table.
        # If you were to create a 'disciplines' table in Supabase, you would use conn.read('disciplines').
        data = {
            "name": ["OT", "SLP", "BC", "ECE", "Assistant/BI"]
        }
    elif list_type == "children":
        # Fetch unique child names from the progress table
        df_progress = get_data("progress")
        if not df_progress.empty:
            data = {"name": df_progress["child_name"].unique().tolist()}
        else:
            data = {"name": []}
    
    # Return as a DataFrame for consistency with previous list functions
    return pd.DataFrame(data)


def save_progress(date, child, discipline, goal, status, notes):
    """Saves a new progress entry."""
    data = [{
        "date": date.isoformat(), 
        "child_name": child, 
        "discipline": discipline, 
        "goal_area": goal, 
        "status": status, 
        "notes": notes,
        # Note: 'media_path' is not included here as your current tracker.py doesn't handle file uploads
    }]
    try:
        conn.insert(table="progress", data=data)
        st.cache_data.clear() # Clear cache so the dashboard updates
        return True
    except Exception as e:
        st.error(f"Error saving progress data: {e}")
        return False


def save_plan(date, lead_staff, support_staff, warm_up, learning_block, regulation_break, social_play, closing_routine, materials_needed, internal_notes):
    """Saves a new daily session plan entry."""
    data = [{
        "date": date, 
        "lead_staff": lead_staff, 
        "support_staff": support_staff, 
        "warm_up": warm_up, 
        "learning_block": learning_block, 
        "regulation_break": regulation_break, 
        "social_play": social_play,
        "closing_routine": closing_routine,
        "materials_needed": materials_needed,
        "internal_notes": internal_notes
    }]
    try:
        conn.insert(table="session_plans", data=data)
        st.cache_data.clear() # Clear cache so the planner view updates
        return True
    except Exception as e:
        st.error(f"Error saving plan data: {e}")
        return False