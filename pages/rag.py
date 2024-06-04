import base64

import streamlit as st
import openai
from dotenv import load_dotenv
load_dotenv()
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
try:
    from llama_index import VectorStoreIndex, Document
except ImportError:
    from llama_index.core import VectorStoreIndex, Document
import os
from pdfminer.high_level import extract_text

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

openai.api_key = st.secrets.openai_key
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Streamlit's open-source Python library!"}
    ]

class PDFReader:
    def __init__(self, input_dir, chunk_size=512):
        self.input_dir = input_dir
        self.chunk_size = chunk_size

    def load_data(self):
        docs = []
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "rb") as f:
                        pdf_content = self.extract_text_from_pdf(f)
                        chunks = self.chunk_text(pdf_content)
                        for i, chunk in enumerate(chunks):
                            doc = Document(text=chunk, extra_info={"file_path": file_path, "chunk_id": i})
                            docs.append(doc)
        return docs

    def extract_text_from_pdf(self, file):
        return extract_text(file)

    def chunk_text(self, text):
        # Split text into chunks of size `self.chunk_size`
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = PDFReader(input_dir="./pdfs", chunk_size=512)  # Adjust chunk size as needed
        docs = reader.load_data()
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on university document library and your job is to answer questions. Assume that all questions are related to the Streamlit Python library. Keep your answers concise and based on facts – do not hallucinate features.")
        index = VectorStoreIndex.from_documents(docs)  # No need to specify chunk size here since chunks are pre-made
        return index

def rag():
    index = load_data()

    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if prompt := st.text_input("Your question"):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display the latest response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
            source_nodes = response.source_nodes  # Fetch relevant sources
            if source_nodes:
                document = source_nodes[0]  # Extract the Document object from NodeWithScore
                source = document.metadata.get("file_path", "Unknown source")
                st.session_state.messages.append({"role": "assistant", "content": response.response, "source": source})
            else:
                st.session_state.messages.append({"role": "assistant", "content": response.response})

    # Layout for source and response
    col1, col2 = st.columns([1, 2])  # Specify the width ratios

    with col1:
        if st.session_state.messages[-1]["role"] == "assistant" and "source" in st.session_state.messages[-1]:
            source_path = st.session_state.messages[-1]["source"]
            source_name = os.path.basename(source_path)

            # Apply custom CSS to style the left panel
            st.markdown(
                f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">'
                f'**Source:** {source_name}'
                f'</div>',
                unsafe_allow_html=True
            )

            def download_file():
                with open(source_path, "rb") as f:
                    contents = f.read()
                st.download_button(label="Download PDF", data=contents, file_name=source_name, mime="application/pdf")

            download_file()

    with col2:
        # Apply custom CSS to style the right panel
        st.markdown(
            '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">'
            f'{st.session_state.messages[-1]["content"]}'
            '</div>',
            unsafe_allow_html=True
        )

if __name__ == '__main__':
    rag()
