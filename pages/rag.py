# Standard library imports
import os

# Third-party library imports
from dotenv import load_dotenv
import streamlit as st
import openai
from pdfminer.high_level import extract_text

# Llama Index imports
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

try:
    from llama_index import VectorStoreIndex, Document
except ImportError:
    from llama_index.core import VectorStoreIndex, Document

# Load environment variables
load_dotenv()

openai.api_key = st.secrets.openai_key


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
                        print(f"Extracted text from {file_path}")
                        chunks = self.chunk_text(pdf_content)
                        print(f"Created {len(chunks)} chunks for {file_path}")
                        for i, chunk in enumerate(chunks):
                            doc = Document(text=chunk, extra_info={"file_path": file_path, "chunk_id": i})
                            docs.append(doc)
        return docs

    def extract_text_from_pdf(self, file):
        extracted_text = extract_text(file)
        print("Extracted text from PDF")
        return extracted_text

    def chunk_text(self, text):
        # Split text into chunks of size `self.chunk_size`
        words = text.split()
        chunks = [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]
        print(f"Chunked text into {len(chunks)} chunks")
        return chunks

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = PDFReader(input_dir="./pdfs", chunk_size=512)  # Adjust chunk size as needed
        docs = reader.load_data()
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5,
                              system_prompt="You are an expert on university document library and your job is to "
                                            "answer questions. Assume that all questions are related to the Streamlit "
                                            "Python library. Keep your answers concise and based on facts – do not "
                                            "hallucinate features.")
        index = VectorStoreIndex.from_documents(docs)  # No need to specify chunk size here since chunks are pre-made
        return index


def rag():
    index = load_data()

    if "chat_engine" not in st.session_state:
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if prompt := st.text_input("Your question"):
        st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
            source_nodes = response.source_nodes
            if source_nodes:
                sources = []
                for document in source_nodes:
                    source_path = document.metadata.get("file_path", "Unknown source")
                    sources.append(os.path.basename(source_path))
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.response, "sources": sources})
            else:
                st.session_state.messages.append({"role": "assistant", "content": response.response})

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.session_state.messages[-1]["role"] == "assistant" and "sources" in st.session_state.messages[-1]:
            sources = st.session_state.messages[-1]["sources"]
            if sources:
                st.markdown(
                    f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">'
                    f'**Sources:**'
                    f'<ul>'
                    f'{"".join([f"<li>{source}</li>" for source in sources])}'
                    f'</ul>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                def download_files():
                    for source in sources:
                        source_path = os.path.join("pdfs", source)
                        with open(source_path, "rb") as f:
                            contents = f.read()
                        st.download_button(label=f"Download {source}", data=contents, file_name=source,
                                           mime="application/pdf")

                download_files()

    with col2:
        st.markdown(
            '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">'
            f'{st.session_state.messages[-1]["content"]}'
            '</div>',
            unsafe_allow_html=True
        )


if __name__ == '__main__':
    rag()
