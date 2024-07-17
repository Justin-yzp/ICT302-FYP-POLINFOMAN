import os
import time
import streamlit as st
from openai import OpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.core import Settings, VectorStoreIndex, Document
from utils.pdf_reader import PDFReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

client = OpenAI(api_key=st.secrets.openai_key)


def clear_specific_cache():
    keys_to_clear = ["cache_key", "chat_engine", "previous_response"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def clear_all_cache():
    keys_to_clear = ["cache_key", "chat_engine", "chunk_size", "docs", "pdf_files", "previous_response",
                     "preloaded_data"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.cache_resource.clear()
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

        Settings.llm = LlamaOpenAI(model="gpt-3.5-turbo", temperature=0.5,
                                   system_prompt="You are an expert on university document library. Answer questions based on the provided information.")
        index = VectorStoreIndex.from_documents(docs)

        end_time = time.time()
        processing_time = end_time - start_time
        st.write(f"Processing time: {processing_time:.2f} seconds")

        return index, docs


@st.cache_resource(show_spinner=False)
def preload_all_precision_levels(pdf_files):
    precision_levels = {
        "Low": (200, 20),
        "Medium": (100, 10),
        "High": (50, 5)
    }

    preloaded_data = {}
    for precision, (chunk_size, overlap_size) in precision_levels.items():
        cache_key = generate_cache_key(chunk_size, overlap_size, pdf_files)
        index, docs = load_data_with_chunk_size(chunk_size, overlap_size, cache_key)
        preloaded_data[precision] = {
            "index": index,
            "docs": docs,
            "chat_engine": index.as_chat_engine(chat_mode="condense_question", verbose=True)
        }
    return preloaded_data


def is_valid_query(query):
    return bool(re.search(r'\b[a-zA-Z]{3,}\b', query))


def calculate_accuracy_score(query, response, source_nodes):
    if not is_valid_query(query):
        return 0.0

    # Check for null or error responses
    if "unable to provide an answer" in response.lower() or not response.strip():
        return 0.0

    # Calculate relevance score
    vectorizer = TfidfVectorizer().fit([query, response])
    vectors = vectorizer.transform([query, response])
    relevance_score = cosine_similarity(vectors[0], vectors[1])[0][0]

    # Calculate source relevance
    source_relevance = np.mean([node.score for node in source_nodes]) if source_nodes else 0

    # Combine scores (you may want to adjust weights)
    combined_score = (relevance_score * 0.7 + source_relevance * 0.3) * 100

    return min(combined_score, 100)  # Ensure score doesn't exceed 100


def ai_review_score(query, response, initial_score, context):
    if not is_valid_query(query):
        return 0.0

    prompt = f"""
    Given the following question, answer, and context, review the initial relevance score and adjust if necessary.

    Question: {query}
    Answer: {response}
    Context: {context}
    Initial relevance score: {initial_score}

    Your task:
    1. Determine if the question is nonsensical, random characters, or unrelated to the provided context.
    2. If the question is nonsensical, random characters, or unrelated to the context, score it as 0.
    3. If the answer cannot be derived from the given context, score it as 0.
    4. Otherwise, analyze the relevance of the answer to the question based ONLY on the provided context.
    5. Consider the initial score provided, but prioritize your own assessment based on the context.
    6. Provide your own relevance score (0-100) based on your analysis.
    7. Briefly explain your scoring decision.

    Important rules:
    - Only consider information from the provided context. Do not use external knowledge.
    - If the question cannot be answered using the given context, the score should be 0.
    - General questions not specific to the context (e.g., "What is life?") should be scored 0.

    Output your response in the following format:
    Score: [Your score]
    Explanation: [Your explanation]
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert at evaluating the relevance of answers to questions."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_response = response.choices[0].message.content
    score_line = [line for line in ai_response.split('\n') if line.startswith("Score:")][0]
    ai_score = float(score_line.split(":")[1].strip())

    return ai_score


def get_accuracy_color(score):
    if score < 33:
        return "red"
    elif score < 66:
        return "orange"
    else:
        return "green"


def rag():
    clear_specific_cache()
    st.title("University Document Library")
    st.markdown(
        """
        <div style="background-color: rgba(233, 233, 233, 0.4); padding: 15px; border-radius: 10px; margin-bottom: 20px; backdrop-filter: blur(10px);">
        <h3 style="text-align: center;">Welcome to the University Document Library</h3>
        <p style="text-align: center;">
            Use this tool to search through university documents and get precise answers to your questions.
        </p>
        </div>
        """, unsafe_allow_html=True)

    current_pdf_files = get_pdf_files()

    if "preloaded_data" not in st.session_state or set(st.session_state.pdf_files) != set(current_pdf_files):
        st.session_state.preloaded_data = preload_all_precision_levels(current_pdf_files)
        st.session_state.pdf_files = current_pdf_files

    st.write("Select precision level:")
    col1, col2 = st.columns([3, 1])

    with col1:
        precision = st.radio(
            "Precision",
            options=["Low", "Medium", "High"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with col2:
        if st.button("Clear Cache"):
            clear_all_cache()
            st.success("Cache cleared successfully!")
            st.rerun()

    # Use preloaded data
    preloaded_data = st.session_state.preloaded_data[precision]
    index = preloaded_data["index"]
    docs = preloaded_data["docs"]
    chat_engine = preloaded_data["chat_engine"]

    st.session_state.chat_engine = chat_engine
    st.session_state.docs = docs

    st.markdown(
        """
        <div style="background-color: rgba(233, 233, 233, 0.4); padding: 15px; border-radius: 10px; margin-bottom: 20px; backdrop-filter: blur(10px);">
        <h4>Ask a Question</h4>
        <p>Enter your question below and get answers based on the university documents.</p>
        </div>
        """, unsafe_allow_html=True)

    prompt = st.text_input("Your question")

    if prompt:
        clear_specific_cache()
        chat_engine = preloaded_data["index"].as_chat_engine(chat_mode="condense_question", verbose=True)
        # Use this chat_engine for the current query
        if not is_valid_query(prompt):
            st.warning("Please enter a valid question or query.")
            return

        # clear_specific_cache()

        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)

            if not response.response.strip():
                st.warning("I couldn't find any relevant information to answer your query.")
                return

            source_nodes = response.source_nodes
            context = "\n".join([node.node.text for node in source_nodes])
            initial_accuracy_score = calculate_accuracy_score(prompt, response.response, source_nodes)

            # AI review of the score
            ai_score = ai_review_score(prompt, response.response, initial_accuracy_score, context)

            # Use AI score directly
            final_accuracy_score = ai_score

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
                    "contexts": context_snippets,
                    "accuracy_score": final_accuracy_score
                }
            else:
                st.session_state.previous_response = {
                    "content": response.response,
                    "accuracy_score": final_accuracy_score
                }

    col1, col2 = st.columns([1, 2])

    with col1:
        if 'previous_response' in st.session_state:
            accuracy_score = st.session_state.previous_response.get("accuracy_score", 0)
            if accuracy_score >= 5:  # Only show sources if the score is 5 or above
                sources = st.session_state.previous_response.get("sources", [])
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
            else:
                st.markdown(
                    '<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; color: #FF0000;">'
                    '<strong>Sources:</strong><br>'
                    'No sources available as the query is not relevant.'
                    '</div>',
                    unsafe_allow_html=True
                )

    with col2:
        if 'previous_response' in st.session_state:
            accuracy_score = st.session_state.previous_response.get("accuracy_score", 0)
            if accuracy_score < 5:  # Threshold for very low relevance
                st.warning("The query doesn't seem to be relevant to the available information.")
            else:
                accuracy_color = get_accuracy_color(accuracy_score)
                st.markdown(
                    f'''
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Estimated Relevance:</strong><br>
                        <div style="background-color: #e0e0e0; border-radius: 5px; height: 20px; width: 100%;">
                            <div style="background-color: {accuracy_color}; width: {accuracy_score}%; height: 100%; border-radius: 5px;"></div>
                        </div>
                        <span>{accuracy_score:.2f}% (This score indicates the estimated relevance of the response, not its factual accuracy)</span>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">'
                    '<strong>Response:</strong><br>'
                    f'{st.session_state.previous_response["content"]}'
                    '</div>',
                    unsafe_allow_html=True
                )

                if "contexts" in st.session_state.previous_response:
                    with st.expander("View Context Snippets"):
                        for source, context in st.session_state.previous_response["contexts"]:
                            st.markdown(f"**Source: {source}**")
                            st.text_area("Context:", value=context, height=150, disabled=True)
                            st.markdown("---")


if __name__ == '__main__':
    rag()
