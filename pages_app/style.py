# pages_app/style.py

import streamlit as st
import base64


def apply_custom_styles():
    # Custom CSS
    st.markdown("""
        <style>
        .custom-title {
            font-size: 24px;
            color: #ff6347;
            text-align: center;
        }
        .custom-button {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
        }
        .custom-container {
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Background image
    with open("elements/background.jpg", "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <style>
        body {{
            background-image: url('data:image/jpg;base64,{b64_image}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)
