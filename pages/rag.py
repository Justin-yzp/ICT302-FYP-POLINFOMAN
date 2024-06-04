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
    def __init__(self, input_dir):
        self.input_dir = input_dir

    def load_data(self):
        docs = []
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "rb") as f:
                        pdf_content = self.extract_text_from_pdf(f)
                        doc = Document(text=pdf_content)
                        docs.append(doc)
        return docs

    def extract_text_from_pdf(self, file):
        return extract_text(file)

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = PDFReader(input_dir="./pdfs")
        docs = reader.load_data()
        for doc in docs:
            doc.extra_info["file_path"] = doc.text[:512]  # Store file path as metadata
            doc.text = ""  # Clear text to save memory
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on university document library and your job is to answer questions. Assume that all questions are related to the Streamlit Python library. Keep your answers concise and based on facts – do not hallucinate features.")
        index = VectorStoreIndex.from_documents(docs, chunk_size=16384)  # Increase the chunk size
        return index


def rag():
    index = load_data()

    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Display the prior chat messages
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "source" in message:
                st.write(f"**Source:** {message['source']}\n{message['content']}")
            else:
                st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
                source_nodes = response.source_nodes  # Fetch relevant sources
                if source_nodes:
                    document = source_nodes[0]  # Extract the Document object from NodeWithScore
                    source = document.metadata.get("file_path", "Unknown source")
                    st.write(f"**Source:** {source}\n{response.response}")
                    message = {"role": "assistant", "content": response.response, "source": source}
                else:
                    st.write(response.response)
                    message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)  # Add response to message history

if __name__ == '__main__':
    rag()
