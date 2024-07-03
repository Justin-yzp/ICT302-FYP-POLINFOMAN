import streamlit as st
from auth.login import login
from pages_app.rag import rag
from pages_app.register import register
from utils.calendar_dashboard import Calendar
from pages_app.style import apply_custom_styles, set_background_image
from pages_app.welcome import welcome
from pages_app.about import about

# Apply custom styles
apply_custom_styles()

# Set background image
set_background_image("https://raw.githubusercontent.com/Justin-yzp/ICT302-new/main/images/background.jpg")

# Initialize session state if it doesn't exist
if 'page' not in st.session_state:
    st.session_state['page'] = 'welcome'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

# Logout function
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'welcome'
    st.session_state['is_admin'] = False
    st.rerun()

# Function to display the appropriate page based on session state
def display_page():
    pages = {
        'welcome': welcome,
        'login': login,
        'dashboard': lambda: display_calendar('users.db'),
        'rag': rag,
        'register': register,
        'about': about
    }
    page_function = pages.get(st.session_state['page'])
    if page_function:
        page_function()

# Function to display calendar page
def display_calendar(db_path):
    cal = Calendar(db_path)
    cal.display_calendar()

# Sidebar navigation items
sidebar_items_logged_out = {
    '🏠 Welcome': 'welcome',
    '🔒 Login': 'login',
    '📘 About': 'about'
}

sidebar_items_logged_in = {
    '🏠 Welcome': 'welcome',
    '📅 Dashboard': 'dashboard',
    '🔍 RAG': 'rag',
    '📝 Register': 'register',
    '📘 About': 'about'

}

sidebar_items = sidebar_items_logged_out if not st.session_state['logged_in'] else sidebar_items_logged_in

# Display sidebar for navigation with emojis
selected_page = st.sidebar.radio("Navigation", list(sidebar_items.keys()))

# Update session state based on selected page
if selected_page == 'Logout':
    logout()
else:
    st.session_state['page'] = sidebar_items[selected_page]

# Display the appropriate page
if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")  # Display login status in the sidebar
else:
    st.sidebar.write("Not Logged in")

display_page()

# Add logout button at the bottom of the sidebar
if st.session_state['logged_in']:
    st.sidebar.markdown('---')
    st.sidebar.button("Logout", key="logout_btn", on_click=logout)
