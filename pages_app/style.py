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
    }}
    /* Rest of your CSS styles */
    </style>
    """,
        unsafe_allow_html=True
    )
def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp {
            font-family: 'Arial', sans-serif;
        }
        .stButton > button {
            color: #4F8BF9;
            border-radius: 20px;
            height: 3em;
            width: 100%;
        }
        .stTextInput > div > div > input {
            color: #4F8BF9;
        }
        .stMarkdown {
            color: white;
            text-shadow: 1px 1px 2px black;
        }
        </style>
    """, unsafe_allow_html=True)
