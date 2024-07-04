import streamlit as st


def welcome():
    st.markdown('<h1 class="title">University Document Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subtitle">Your Intelligent Guide for University Documents</h2>', unsafe_allow_html=True)

    st.markdown("""
    <div class="content card">
        <p>Welcome to the University Document Assistant! Our AI-driven system simplifies your document management:</p>
        <ul>
            <li>Get quick answers to your questions</li>
            <li>Navigate complex university documents effortlessly</li>
            <li>Download source PDFs directly</li>
            <li>Stay organized with an interactive calendar</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="additional-info card">
        <p>Our University Document Assistant is designed to help you with:</p>
        <ul>
            <li><strong>Efficient Searching:</strong> Quickly find the information you need within extensive documents.</li>
            <li><strong>Interactive Features:</strong> Use our calendar to track important dates and deadlines.</li>
            <li><strong>Ease of Access:</strong> Download and view documents anytime, anywhere.</li>
            <li><strong>AI-Powered Assistance:</strong> Leverage AI to get explanations and summaries of complex topics.</li>
        </ul>
        <p>Explore all these features and more to make your university life easier and more organized.</p>
    </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    welcome()
