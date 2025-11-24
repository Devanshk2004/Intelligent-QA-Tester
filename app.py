import streamlit as st
import os
import shutil
from vector_db import process_and_store_documents
from llm_helper import ask_bot 

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

st.title("🤖 Autonomous QA Agent")
st.markdown("### Upload Project Docs & Build Testing Brain")

with st.sidebar:
    st.header("📁 Data Ingestion")
    
    uploaded_files = st.file_uploader(
        "Upload Support Docs & Checkout.html", 
        type=["pdf", "md", "txt", "json", "html"], 
        accept_multiple_files=True
    )

    if st.button("Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Parsing documents & Creating Embeddings..."):
                try:
                    if os.path.exists("chroma_db"):
                        shutil.rmtree("chroma_db")
                    
                    status = process_and_store_documents(uploaded_files)
                    st.success(status)
                    st.session_state["kb_ready"] = True
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please upload files first!")

if not os.path.exists("chroma_db"):
    st.info("👈 Please upload documents in the sidebar and click 'Build Knowledge Base' to start.")
    st.stop() 

st.divider()
st.subheader("🕵️ Test Case Generator Agent")
st.caption("Ask the AI to generate test cases based on your uploaded documents.")

user_query = st.chat_input("Ex: Generate test cases for discount code feature...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_bot(user_query)
            st.markdown(response)