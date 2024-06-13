import streamlit as st
from utils.calendar_dashboard import CalendarDashboard
import os

# Set page configuration at the beginning of the script
st.set_page_config(layout="wide")

def display_calendar_page():
    # Connect to the SQLite database (or create it if it doesn't exist)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_path, 'users.db')
    cal_dashboard = CalendarDashboard(db_path)
    cal_dashboard.display_calendar()
    cal_dashboard.close_connection()

def dashboard():
    display_calendar_page()

dashboard()
