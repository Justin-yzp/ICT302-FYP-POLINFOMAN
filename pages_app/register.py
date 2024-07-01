import streamlit as st
from pages_app.admin_user_management import admin_user_management
from pages_app.pdf_management import pdf_management

def register():
    st.title("Welcome to the Application")
    st.write("Please select an option to proceed.")

    col1 = st.empty()  # Use a single column for admin functions

    with col1:
        st.subheader("Admin Functions")

        # Dropdown menu for admin functions
        admin_function = st.selectbox("Select an admin function", ["Select", "Admin User Management", "PDF Management"])

        if admin_function == "Admin User Management":
            st.session_state['page'] = 'admin_user_management'
        elif admin_function == "PDF Management":
            st.session_state['page'] = 'pdf_management'

    # Navigation logic based on session state
    if st.session_state.get('page') == 'admin_user_management':
        admin_user_management()
    elif st.session_state.get('page') == 'pdf_management':
        pdf_management()

if __name__ == "__main__":
    register()
