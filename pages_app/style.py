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
            color: #FFFFFF;
        }
        header {
            background-color: transparent !important;
        }
        .stApp > header {
            background-color: transparent !important;
        }
        .stApp {
            margin-top: -80px;  /* Adjust this value as needed */
        }
        
        /* Additional style to ensure content isn't hidden behind header */
        .main .block-container {
            padding-top: 80px;  /* Adjust this value as needed */
        }
        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }
        

        /* Buttons */
        .stButton > button {
            color: #FFFFFF;
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

        /* Text inputs */
        .stTextInput > div > div > input {
            color: #FFFFFF;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
            backdrop-filter: blur(5px);
        }

        /* Select boxes */
        .stSelectbox > div > div > div {
            color: #FFFFFF;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            backdrop-filter: blur(5px);
        }

        /* Markdown text */
        .stMarkdown {
            color: #FFFFFF;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }

        /* Dataframes */
        .dataframe {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
            backdrop-filter: blur(5px);
        }
        .dataframe th {
            background-color: rgba(79, 139, 249, 0.7);
            color: white;
        }
        .dataframe td {
            background-color: rgba(255, 255, 255, 0.1);
            color: #FFFFFF;
        }

        /* Slider */
        .stSlider > div > div > div > div {
            background-color: rgba(79, 139, 249, 0.7);
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
        }

        /* Custom classes for flexible use */
        .highlight {
            background-color: rgba(255, 215, 0, 0.7);
            padding: 5px;
            border-radius: 5px;
            color: #000000;
        }
        .card {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(5px);
        }

        /* Additional styles for better integration */
        .stTextArea textarea {
            color: #FFFFFF;
            background-color: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(5px);
        }
        .stCheckbox label {
            color: #FFFFFF;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }
        .stRadio label {
            color: #FFFFFF;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }
        .stProgress > div > div > div > div {
            background-color: rgba(79, 139, 249, 0.7);
        }
        </style>
    """, unsafe_allow_html=True)