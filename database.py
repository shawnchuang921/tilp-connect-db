# views/database.py (SUPABASE VERSION)
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text

# Initialize connection using the secrets.toml configuration
conn = st.connection("supabase_db", type="sql")

def init_db():
    # Tables are already created in Supabase via SQL Editor
    pass

# --- CORE DB FUNCTIONS ---

def get_user(username, password):
    """Retrieves user details for login."""
    try:
        df = conn.query("SELECT * FROM users WHERE username = :u AND password = :p", 
                        params={"u": username, "p": password}, ttl=0)
        if not df.empty:
            return df.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

def get_data(table_name):
    """Retrieves all data from a table."""
    try:
        # ttl=0 ensures we always get fresh data
        return conn.query(f"SELECT * FROM {table_name}", ttl=0)
    except Exception:
        return pd.DataFrame()

def get_list_data(table_name):
    return get_data(table_name)

# --- CRUD Functions ---

def upsert_user(username, password, role, child_link):
    try:
        with conn.session as s:
            if password:
                s.execute(
                    text("INSERT INTO users (username, password, role, child_link) VALUES (:u, :p, :r, :c) "
                         "ON CONFLICT (username) DO UPDATE SET password = :p, role = :r, child_link = :c"),
                    {"u": username, "p": password, "r": role, "c": child_link}
                )
            else:
                # Update without changing password
                s.execute(
                    text("UPDATE users SET role = :r, child_link = :c WHERE username = :u"),
                    {"u": username, "r": role, "c": child_link}
                )
            s.commit()
    except Exception as e:
        st.error(f"Error saving user: {e}")

def delete_user(username):
    try:
        with conn.session as s:
            s.execute(text("DELETE FROM users WHERE username = :u"), {"u": username})
            s.commit()
    except Exception as e:
        st.error(f"Error deleting user: {e}")

def upsert_child(child_name, parent_username, date_of_birth=None):
    try:
        with conn.session as s:
            s.execute(
                text("INSERT INTO children (child_name, parent_username, date_of_birth) VALUES (:c, :p, :d) "
                     "ON CONFLICT (child_name) DO UPDATE SET parent_username = :p, date_of_birth = :d"),
                {"c": child_name, "p": parent_username, "d": date_of_birth}
            )
            s.commit()
    except Exception as e:
        st.error(f"Error saving child: {e}")

def delete_child(child_name):
    try:
        with conn.session as s:
            # Clear parent link first
            s.execute(text("UPDATE users SET child_link = 'All' WHERE child_link = :c"), {"c": child_name})
            # Delete child
            s.execute(text("DELETE FROM children WHERE child_name = :c"), {"c": child_name})
            s.commit()
    except Exception as e:
        st.error(f"Error deleting child: {e}")

def upsert_list_item(table_name, item_name):
    try:
        # Note: table names cannot be parameterized in SQL, be careful with inputs
        valid_tables = ["disciplines", "goal_areas"]
        if table_name not in valid_tables: return
        
        with conn.session as s:
            s.execute(
                text(f"INSERT INTO {table_name} (name) VALUES (:n) ON CONFLICT (name) DO NOTHING"),
                {"n": item_name}
            )
            s.commit()
    except Exception as e:
        st.error(f"Error adding item: {e}")

def delete_list_item(table_name, item_name):
    try:
        valid_tables = ["disciplines", "goal_areas"]
        if table_name not in valid_tables: return
        
        with conn.session as s:
            s.execute(text(f"DELETE FROM {table_name} WHERE name = :n"), {"n": item_name})
            s.commit()
    except Exception as e:
        st.error(f"Error deleting item: {e}")

# --- Progress/Planner Functions ---

def save_progress(date, child, discipline, goal, status, notes, media_path):
    try:
        with conn.session as s:
            s.execute(
                text("INSERT INTO progress (date, child_name, discipline, goal_area, status, notes, media_path) "
                     "VALUES (:d, :c, :di, :g, :s, :n, :m)"),
                {"d": date, "c": child, "di": discipline, "g": goal, "s": status, "n": notes, "m": media_path}
            )
            s.commit()
    except Exception as e:
        st.error(f"Error saving progress: {e}")

def save_plan(date, lead_staff, support_staff, warm_up, learning_block, regulation_break, social_play, closing_routine, materials_needed, internal_notes):
    try:
        with conn.session as s:
            s.execute(
                text("INSERT INTO session_plans (date, lead_staff, support_staff, warm_up, learning_block, regulation_break, "
                     "social_play, closing_routine, materials_needed, internal_notes) "
                     "VALUES (:d, :ls, :ss, :w, :l, :r, :sp, :cr, :m, :i)"),
                {"d": date, "ls": lead_staff, "ss": support_staff, "w": warm_up, "l": learning_block, 
                 "r": regulation_break, "sp": social_play, "cr": closing_routine, "m": materials_needed, "i": internal_notes}
            )
            s.commit()
    except Exception as e:
        st.error(f"Error saving plan: {e}")