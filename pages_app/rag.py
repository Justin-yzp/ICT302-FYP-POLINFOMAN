import os
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, Document
from utils.pdf_reader import PDFReader

openai.api_key = st.secrets.openai_key


@st.cache_resource(show_spinner=False)
def load_data(input_dir="./pdfs", chunk_size=512):
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = PDFReader(input_dir=input_dir, chunk_size=chunk_size)
        docs = reader.load_data()
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5,
                              system_prompt="You are an expert on university document library and your job is to "
                                            "answer questions. Assume that all questions are related to the Streamlit "
                                            "Python library. Keep your answers concise and based on facts – do not "
                                            "hallucinate features.")
        index = VectorStoreIndex.from_documents(docs)
        return index


def rag():
    index = load_data()

    if "chat_engine" not in st.session_state:
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if "processed_chunks" not in st.session_state:
        st.session_state.processed_chunks = {}

    if prompt := st.text_input("Your question"):
        # Clear existing messages when a new question is submitted
        st.session_state.messages = [{"role": "user", "content": prompt}]

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
            source_nodes = response.source_nodes
            if source_nodes:
                sources = []
                for document in source_nodes:
                    source_path = document.metadata.get("file_path", "Unknown source")
                    # Check if source is already in sources list
                    if os.path.basename(source_path) not in sources:
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
                    for i, source in enumerate(sources):
                        source_path = os.path.join("pdfs", source)
                        with open(source_path, "rb") as f:
                            contents = f.read()
                        st.download_button(label=f"Download {source}", data=contents, file_name=source,
                                           mime="application/pdf", key=f"download_{i}")

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