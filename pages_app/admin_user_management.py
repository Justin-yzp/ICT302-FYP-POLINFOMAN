# pages_app/admin_user_management.py
import streamlit as st
import re
from db.db_handler import add_user, get_all_users, update_user, delete_user

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def admin_user_management():
    st.title("Admin User Management")
    st.write("---")

    users = get_all_users()

    col1, col2 = st.columns(2)

    with col1:
        st.write("## Current Users")
        selected_user = st.radio("Select a user to manage", [user[1] for user in users])

    if 'selected_user_id' not in st.session_state:
        st.session_state['selected_user_id'] = None

    if selected_user:
        user_details = next((user for user in users if user[1] == selected_user), None)
        if user_details:
            user_id, username, password = user_details
            st.session_state['selected_user_id'] = user_id

            with col2:
                st.write("## Edit User")
                new_username = st.text_input("Username", value=username, key="edit_username")
                new_password = st.text_input("Password", type="password", key="edit_password")

                if st.button("Update User", key="update_user_btn"):
                    if new_username and new_password:
                        if is_valid_password(new_password):
                            update_user(user_id, new_username, new_password)
                            st.success("User updated successfully")
                        else:
                            st.error("Password must include uppercase, lowercase, number, and special character")
                    else:
                        st.error("Username and Password cannot be empty")

                if st.button("Delete User", key="delete_user_btn"):
                    delete_user(username)
                    st.success("User deleted successfully")

    st.write("---")
    st.write("## Add New User")
    new_user = st.text_input("New Username", key="new_username")
    new_user_password = st.text_input("New Password", type="password", key="new_password")

    if st.button("Add User", key="add_user_btn"):
        if new_user and new_user_password:
            if is_valid_password(new_user_password):
                add_user(new_user, new_user_password)
                st.success("New user added successfully")
            else:
                st.error("Password must include uppercase, lowercase, number, and special character")
        else:
            st.error("New username and password cannot be empty")

if __name__ == "__main__":
    admin_user_management()