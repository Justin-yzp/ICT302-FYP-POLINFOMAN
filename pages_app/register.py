import streamlit as st
import os
from db.db_handler import add_user, get_all_users, update_user, delete_user
from utils.pdf_reader import PDFReader

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_pdf_status(pdf_dir, processed_chunks):
    processed_pdfs = []
    unprocessed_pdfs = []
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                if file_path in processed_chunks:
                    processed_pdfs.append(file)
                else:
                    unprocessed_pdfs.append(file)
    return processed_pdfs, unprocessed_pdfs

def register():
    st.title("Admin User Management")
    st.write("---")

    # Fetch all users from the database
    users = get_all_users()

    col1, col2 = st.columns(2)

    # Display users in a panel
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
                        update_user(user_id, new_username, new_password)
                        st.success("User updated successfully")
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
            add_user(new_user, new_user_password)
            st.success("New user added successfully")
        else:
            st.error("New username and password cannot be empty")

    st.write("---")
    st.button("Logout", key="logout_btn")

    st.write("---")
    st.write("## PDF Management")

    # Directory to store PDFs
    pdf_dir = "pdfs"
    ensure_directory_exists(pdf_dir)

    # Load processed chunks
    pdf_reader = PDFReader(input_dir=pdf_dir)
    processed_chunks = pdf_reader.load_processed_chunks()

    # Load PDF status
    processed_pdfs, unprocessed_pdfs = load_pdf_status(pdf_dir, processed_chunks)

    col3, col4 = st.columns(2)

    # Display PDFs in the directory
    with col3:
        st.write("### Current PDFs")
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            st.write(pdf_file)

        # Upload new PDF
        st.write("### Upload New PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            with open(os.path.join(pdf_dir, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded {uploaded_file.name}")
            if st.button("Refresh Page", key="refresh_page_upload"):
                st.experimental_rerun()

        # Remove selected PDF
        st.write("### Remove PDF")
        if pdf_files:
            pdf_to_remove = st.selectbox("Select a PDF to remove", pdf_files)
            if st.button("Remove PDF", key="remove_pdf_btn"):
                os.remove(os.path.join(pdf_dir, pdf_to_remove))
                st.success(f"Removed {pdf_to_remove}")
                if st.button("Refresh Page", key="refresh_page_remove"):
                    st.experimental_rerun()

    # Display processed and unprocessed PDFs
    with col4:
        st.write("### Processed PDFs")
        if processed_pdfs:
            for pdf in processed_pdfs:
                st.write(pdf)
        else:
            st.write("No processed PDFs.")

        st.write("### Unprocessed PDFs")
        if unprocessed_pdfs:
            for pdf in unprocessed_pdfs:
                st.write(pdf)
        else:
            st.write("No unprocessed PDFs.")

        if st.button("Process All PDFs"):
            pdf_reader.load_data()
            st.success("Processed all PDFs.")
            st.experimental_rerun()

if __name__ == "__main__":
    register()
