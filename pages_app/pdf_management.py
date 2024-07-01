# pages_app/pdf_management.py
import streamlit as st
import os
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

def pdf_management():
    st.title("PDF Management")
    st.write("---")

    pdf_dir = "pdfs"
    ensure_directory_exists(pdf_dir)

    pdf_reader = PDFReader(input_dir=pdf_dir)
    processed_chunks = pdf_reader.load_processed_chunks()

    processed_pdfs, unprocessed_pdfs = load_pdf_status(pdf_dir, processed_chunks)

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Current PDFs")
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            st.write(pdf_file)

        st.write("### Upload New PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            with open(os.path.join(pdf_dir, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded {uploaded_file.name}")
            if st.button("Refresh Page", key="refresh_page_upload"):
                st.rerun()

        st.write("### Remove PDF")
        if pdf_files:
            pdf_to_remove = st.selectbox("Select a PDF to remove", pdf_files)
            if st.button("Remove PDF", key="remove_pdf_btn"):
                os.remove(os.path.join(pdf_dir, pdf_to_remove))
                st.success(f"Removed {pdf_to_remove}")
                if st.button("Refresh Page", key="refresh_page_remove"):
                    st.rerun()

    with col2:
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
            st.rerun()

if __name__ == "__main__":
    pdf_management()