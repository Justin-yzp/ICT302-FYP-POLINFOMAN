# pages_app/style.py
import base64
import requests

import streamlit as st


def set_background_image(image_url):
    response = requests.get(image_url)
    encoded_string = base64.b64encode(response.content).decode()

    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string});
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """,
        unsafe_allow_html=True
    )


def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main app */
        .stApp {
            font-family: 'Arial', sans-serif;
            color: #000000;
            margin-top: 0px;  /* Adjust this value as needed */
        }

        header {
            background-color: transparent !important;
        }

        .stApp > header {
            background-color: transparent !important;
        }

        /* Buttons */
        .stButton > button {
            color: #000000;
            background-color: rgba(79, 139, 249, 0.7);
            border: none;
            border-radius: 20px;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            transition-duration: 0.4s;
            backdrop-filter: blur(5px);
        }

        .stButton > button:hover {
            background-color: rgba(69, 160, 73, 0.7);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(0, 0, 0, 0.1); /* Translucent black background */
            backdrop-filter: blur(10px); /* Blur effect */
            padding: 10px; /* Add padding for better readability */
        }

        /* Text inputs */
        .stTextInput > div > div > input {
            color: #000000;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
            backdrop-filter: blur(5px);
        }
        </style>
    """, unsafe_allow_html=True)


