import streamlit as st
import os
import shutil
import zipfile
import io
from dotenv import load_dotenv
from vector_db import process_and_store_documents
from llm_helper import ask_bot, generate_selenium_script 

load_dotenv() 

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent")

# --- STATE MANAGEMENT ---
if "html_context" not in st.session_state:
    st.session_state["html_context"] = ""
if "kb_ready" not in st.session_state:
    st.session_state["kb_ready"] = False
if "generated_cases" not in st.session_state:
    st.session_state["generated_cases"] = False

# --- HELPER: Create Zip for Demo Data ---
def create_demo_zip():
    """Compresses project_assets into a single zip file for download"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Files to include
        files = ["checkout.html", "product_specs.md", "ui_ux_guide.txt", "api_endpoints.json"]
        for file_name in files:
            file_path = os.path.join("project_assets", file_name)
            if os.path.exists(file_path):
                zf.write(file_path, arcname=file_name)
    return zip_buffer.getvalue()

# --- SIDEBAR: Phase 1 ---
with st.sidebar:
    st.header("📁 1. Data Ingestion")
    
    # 1. File Uploader
    uploaded_files = st.file_uploader(
        "Upload Docs & Checkout.html", 
        type=["pdf", "md", "txt", "json", "html"], 
        accept_multiple_files=True
    )
    
    # 2. Build Button (Moved Up)
    if st.button("Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Processing..."):
                try:
                    if os.path.exists("chroma_db"):
                        shutil.rmtree("chroma_db")
                    
                    status, html_content = process_and_store_documents(uploaded_files)
                    
                    st.success(status)
                    st.session_state["kb_ready"] = True
                    
                    if html_content:
                        st.session_state["html_context"] = html_content
                    else:
                        st.warning("Note: checkout.html not found. Script gen might fail.")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Upload files first!")

    # 3. Demo Data Download (Moved Down)
    if os.path.exists("project_assets"):
        st.markdown("---")
        st.caption("Don't have files? Download demo data:")
        
        zip_data = create_demo_zip()
        
        st.download_button(
            label="📥 Download Demo Assets (.zip)",
            data=zip_data,
            file_name="demo_project_assets.zip",
            mime="application/zip",
            help="Downloads checkout.html and support docs to test this app."
        )

# --- MAIN AREA ---

if not st.session_state["kb_ready"]:
    st.info("👈 Step 1: Upload documents (or download demo data) in the sidebar and click 'Build Knowledge Base'.")
    st.stop()

# --- PHASE 2: Test Case Generator ---
st.subheader("🕵️ 2. Test Case Generator")
user_query = st.chat_input("Ex: Generate test cases for discount code...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_bot(user_query, os.getenv("GEMINI_API_KEY"))
            st.markdown(response)
            st.session_state["generated_cases"] = True

# --- PHASE 3: Selenium Script Generator ---
if st.session_state["generated_cases"]:
    st.divider()
    st.subheader("💻 3. Selenium Script Generator")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_case = st.text_area("Paste a Test Scenario from the table above:")

    with col2:
        st.write("") 
        st.write("") 
        generate_btn = st.button("Generate Script 🚀")

    # Feature: Download checkout.html individually for the script
    if st.session_state["html_context"]:
        st.download_button(
            label="📥 Download checkout.html (For Script)",
            data=st.session_state["html_context"],
            file_name="checkout.html",
            mime="text/html",
            help="Keep this in the same folder as your script."
        )

    if generate_btn and selected_case:
        if not st.session_state["html_context"]:
            st.error("⚠️ checkout.html content is missing! Re-upload it in sidebar.")
        else:
            with st.spinner("Writing Python Code..."):
                script = generate_selenium_script(
                    selected_case, 
                    st.session_state["html_context"], 
                    os.getenv("GEMINI_API_KEY")
                )
                
                st.success("Script Generated!")
                st.code(script, language="python")
                st.caption("Copy this code into a file (e.g., test_checkout.py) and run it!")