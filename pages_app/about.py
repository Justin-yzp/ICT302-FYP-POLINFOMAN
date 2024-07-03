import streamlit as st

def about():
    st.markdown('<h1 class="title">About University Document Assistant</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content card">
        <p>The University Document Assistant is designed to help you efficiently manage and navigate university documents. Our features include:</p>
        <ul>
            <li>AI-driven document search and question answering</li>
            <li>Easy navigation of complex documents</li>
            <li>Downloadable source PDFs</li>
            <li>Interactive calendar for important dates</li>
        </ul>
        <p>Our goal is to simplify your document management tasks and provide you with quick and accurate information.</p>
        <p>For any questions or support, please contact us at support@unidocassistant.com.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="title">Frequently Asked Questions</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content card">
        <div>
            <h3>How does the AI-driven document search work?</h3>
            <p>Our AI uses advanced natural language processing to understand your queries and find the most relevant information within your documents.</p>
        </div>
        <div>
            <h3>Can I download the source PDFs?</h3>
            <p>Yes, you can easily download the source PDFs from our platform.</p>
        </div>
        <div>
            <h3>How do I navigate complex documents?</h3>
            <p>We provide an intuitive interface with search and navigation tools to help you find the information you need quickly and easily.</p>
        </div>
        <div>
            <h3>What kind of support is available?</h3>
            <p>You can contact our support team at support@unidocassistant.com for any questions or assistance you need.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


