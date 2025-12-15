# views/tracker.py (UPDATED to fetch lists dynamically)
import streamlit as st
from datetime import date
# Using relative import for database
from .database import save_progress, get_list_data 

def show_page():
    st.header("📝 Client Progress Tracker")
    st.info("Log daily outcomes for clients here. This feeds the Dashboard.")

    # --- Fetch dynamic lists for dropdowns ---
    children = get_list_data("children")["name"].tolist()
    disciplines = get_list_data("disciplines")["name"].tolist()
    
    # Add hardcoded children if none are in the DB yet (or use your master list)
    if not children:
        children = ["Shawn", "Tony", "Regina", "Zoe", "Leo", "Tiffany"]

    if not disciplines:
        disciplines = ["OT", "SLP", "BC", "ECE"]
    # ----------------------------------------
        
    # Form to prevent reloading on every click
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.date_input("Date", date.today())
            child = st.selectbox("Child Name", children)
            discipline = st.selectbox("Discipline", disciplines)
        
        with col2:
            goal_area = st.selectbox("Goal Area", ["Regulation", "Communication", "Fine Motor", "Social Play", "Feeding", "ADLs", "Behavior", "Sensory processing"])
            status = st.select_slider("Performance Status", options=["Regression", "Stable", "Progress"], value="Stable")
        
        notes = st.text_area("Anecdotal Notes", placeholder="e.g., Used spoon independently for 3 scoops...")
        
        submitted = st.form_submit_button("💾 Save Entry")
        
        if submitted:
            # save_progress now returns a boolean for success
            if save_progress(date_input, child, discipline, goal_area, status, notes):
                st.success(f"Data saved for {child}!")
            else:
                st.error("Failed to save data to Supabase.")