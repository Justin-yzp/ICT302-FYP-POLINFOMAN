# pages_app/welcome.py
import streamlit as st

def welcome():
    st.title("Welcome to the Application!")
    st.write("This is a welcome page. Please log in to continue.")
    if st.button("Go to Login"):
        st.session_state['page'] = 'login'
        st.rerun()
