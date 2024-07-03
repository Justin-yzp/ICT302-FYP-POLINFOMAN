import os
import time
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, Document
from utils.pdf_reader import PDFReader

openai.api_key = st.secrets.openai_key


def clear_specific_cache():
    # Clear specific session state items
    keys_to_clear = ["cache_key", "chat_engine", "previous_response"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def clear_all_cache():
    # Clear session state
    keys_to_clear = ["cache_key", "chat_engine", "chunk_size", "docs", "pdf_files", "previous_response"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Clear all st.cache_resource entries
    st.cache_resource.clear()

    # Clear all st.cache_data entries
    st.cache_data.clear()


def generate_cache_key(chunk_size, overlap_size, pdf_files):
    return f"cache_{chunk_size}_{overlap_size}_{','.join(sorted(pdf_files))}"


def get_pdf_files():
    return [f for f in os.listdir("./pdfs") if f.endswith('.pdf')]


@st.cache_resource(show_spinner=False)
def load_data_with_chunk_size(chunk_size, overlap_size, cache_key):
    start_time = time.time()
    with st.spinner(text="Loading and indexing the docs – hang tight! This should take 1-2 minutes."):
        reader = PDFReader(input_dir="./pdfs", chunk_size=chunk_size, overlap_size=overlap_size)
        docs = reader.load_data()

        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5,
                              system_prompt="You are an expert on university document library. Answer questions based on the provided information.")
        index = VectorStoreIndex.from_documents(docs)

        end_time = time.time()
        processing_time = end_time - start_time
        st.write(f"Processing time: {processing_time:.2f} seconds")

        return index, docs


def rag():
    precision = st.radio("Select precision level:", ["Low", "Medium", "High"])

    if precision == "Low":
        chunk_size, overlap_size = 200, 20
    elif precision == "Medium":
        chunk_size, overlap_size = 100, 10
    else:  # High precision
        chunk_size, overlap_size = 50, 5

    # Get current PDF files
    current_pdf_files = get_pdf_files()

    # Check if precision changed or if PDF files changed
    if ("previous_precision" not in st.session_state or
            st.session_state.previous_precision != precision or
            "pdf_files" not in st.session_state or
            set(st.session_state.pdf_files) != set(current_pdf_files)):
        clear_all_cache()

    st.session_state.previous_precision = precision
    st.session_state.pdf_files = current_pdf_files

    cache_key = generate_cache_key(chunk_size, overlap_size, current_pdf_files)
    st.session_state.cache_key = cache_key

    index, docs = load_data_with_chunk_size(chunk_size, overlap_size, cache_key)

    if "chat_engine" not in st.session_state or st.session_state.chunk_size != chunk_size:
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
        st.session_state.chunk_size = chunk_size
        st.session_state.docs = docs

    prompt = st.text_input("Your question")
    if prompt:
        # Clear specific cache items when a new question is asked
        clear_specific_cache()

        with st.spinner("Thinking..."):
            response = index.as_chat_engine(chat_mode="condense_question", verbose=True).chat(prompt)
            source_nodes = response.source_nodes
            if source_nodes:
                sources = []
                context_snippets = []
                for node in source_nodes:
                    source_path = node.node.extra_info.get('file_path', "Unknown source")
                    source_file = os.path.basename(source_path)
                    if source_file not in sources:
                        sources.append(source_file)
                    context_snippets.append((source_file, node.node.text))

                st.session_state.previous_response = {
                    "content": response.response,
                    "sources": sources,
                    "contexts": context_snippets
                }
            else:
                st.session_state.previous_response = {
                    "content": response.response
                }

    col1, col2 = st.columns([1, 2])

    with col1:
        if 'previous_response' in st.session_state and "sources" in st.session_state.previous_response:
            sources = st.session_state.previous_response["sources"]
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
        if 'previous_response' in st.session_state:
            st.markdown(
                '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">'
                f'{st.session_state.previous_response["content"]}'
                '</div>',
                unsafe_allow_html=True
            )

            if "contexts" in st.session_state.previous_response:
                st.markdown(
                    '<div style="background-color: #e9e9e9; padding: 10px; border-radius: 5px;">'
                    '<strong>Context Snippets:</strong>'
                    '<ul>'
                    f'{"".join([f"<li><strong>{source}:</strong> {context}</li>" for source, context in st.session_state.previous_response["contexts"]])}'
                    '</ul>'
                    '</div>',
                    unsafe_allow_html=True
                )


if __name__ == '__main__':
    rag()