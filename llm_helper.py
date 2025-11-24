import os
from dotenv import load_dotenv
from google import genai 
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv() 

MODEL_NAME = "gemini-2.5-flash" 

def get_vector_store():
    """Helper to connect to DB"""
    if not os.path.exists("chroma_db"):
        return None
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="chroma_db", embedding_function=embedding_model)

def ask_bot(query, api_key=None):
    """Phase 2: Test Case Generation (Fixed for Clean Table)"""
    try:
        client = genai.Client(api_key=api_key)
        vectorstore = get_vector_store()
        if not vectorstore:
            return "Knowledge Base not found. Please build it first."
        
        docs = vectorstore.similarity_search(query, k=3)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        full_prompt = f"""
        Act as a QA Test Case Generator.
        Based on the Context provided, generate a Test Case table for the User Request.

        CONTEXT:
        {context_text}

        USER REQUEST:
        {query}

        STRICT OUTPUT RULES:
        1. Output ONLY a Markdown Table.
        2. Do NOT write any introductory text (like "Here are the test cases").
        3. Do NOT write any conclusion or explanations.
        4. The Table MUST have these exact columns: | Test_ID | Feature | Test_Scenario | Expected_Result | Grounded_In |
        5. Write all text in simple text format
        """

        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_selenium_script(test_case, html_code, api_key=None):
    """Phase 3: Selenium Script Generation (Smart & Concise)"""
    try:
        client = genai.Client(api_key=api_key)
        
        vectorstore = get_vector_store()
        doc_context = ""
        if vectorstore:
            docs = vectorstore.similarity_search(test_case, k=2)
            doc_context = "\n\n".join([doc.page_content for doc in docs])
        
        # --- SMART & CONCISE PROMPT ---
        prompt = f"""
        Act as a QA Automation Expert. Write a Python Selenium script.
        
        TEST CASE: "{test_case}"
        RULES: {doc_context}
        HTML:
        ```html
        {html_code}
        ```
        
        REQUIREMENTS:
        1. **Setup:** Use `webdriver_manager` to install Chrome driver.
        2. **Path:** Check if 'checkout.html' is in the current folder OR 'project_assets' folder. Load the one found.
        3. **Code:** Use `webdriver.Chrome()`, `WebDriverWait`, and Assertions.
        4. **Output:** Return ONLY the Python code block.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt
        )
        
        return response.text

    except Exception as e:
        return f"Error generating script: {str(e)}"