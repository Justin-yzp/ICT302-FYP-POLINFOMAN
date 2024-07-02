import streamlit as st
import base64
from auth.login import login
from pages_app.rag import rag
from pages_app.register import register
from utils.calendar_dashboard import Calendar
from pages_app.style import apply_custom_styles, set_background_image
from pages_app.welcome import welcome

# Uncomment to apply wide layout
# st.set_page_config(layout="wide")

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

# Logout button
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'welcome'
    st.session_state['is_admin'] = False
    st.rerun()

# Function to display the appropriate page based on session state
def display_page():
    if st.session_state['page'] == 'welcome':
        welcome()
    elif st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'dashboard':
        db_path = 'users.db'
        cal = Calendar(db_path)
        cal.display_calendar()  # Display the calendar page
    elif st.session_state['page'] == 'rag':
        st.title("RAG Retrieval Augmented Generation")
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Ask me a question about university documents!"}
            ]
        rag()
    elif st.session_state['page'] == 'register' and st.session_state['is_admin']:
        register()

# Display the appropriate page
if st.session_state['logged_in']:
    st.write(f"Logged in as {st.session_state['username']}")

    # Create navigation tabs
    tab_map = {
        'Dashboard': 'dashboard',
        'RAG': 'rag'
    }

    if st.session_state['is_admin']:
        tab_map['Register'] = 'register'

    selected_tab = st.selectbox("Navigation", list(tab_map.keys()))

    # Update session state based on selected tab
    st.session_state['page'] = tab_map[selected_tab]
    display_page()

    # Logout button
    if st.button("Logout", key="logout_btn"):
        logout()
else:
    display_page()