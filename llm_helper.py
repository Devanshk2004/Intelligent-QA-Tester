import os
from dotenv import load_dotenv
from google import genai 
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv() 

# Configuration
MODEL_NAME = "gemini-2.5-flash" 

def get_vector_store():
    """Helper to connect to DB"""
    if not os.path.exists("chroma_db"):
        return None
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="chroma_db", embedding_function=embedding_model)

def ask_bot(query, api_key=None):
    """Phase 2: Test Case Generation"""
    try:
        # 1. Init Client
        client = genai.Client(api_key=api_key) # uses env if api_key is None

        # 2. Retrieve Context
        vectorstore = get_vector_store()
        if not vectorstore:
            return "Knowledge Base not found. Please build it first."
        
        docs = vectorstore.similarity_search(query, k=3)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # 3. Prompt
        full_prompt = f"""You are an expert QA Automation Engineer.
        Your task is to generate comprehensive Test Cases based STRICTLY on the provided context.

        GUIDELINES:
        1. Use ONLY the provided context. Do not invent features.
        2. Format the output as a Markdown Table.
        3. The table MUST have these columns: Test_ID, Feature, Test_Scenario, Expected_Result, Grounded_In.
        4. 'Grounded_In' column must cite the specific document name.

        CONTEXT:
        {context_text}

        USER REQUEST:
        {query}

        ANSWER (Markdown Table):
        """

        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_selenium_script(test_case, html_code, api_key=None):
    """Phase 3: Selenium Script Generation (Now with RAG!)"""
    try:
        client = genai.Client(api_key=api_key)
        
        vectorstore = get_vector_store()
        doc_context = ""
        if vectorstore:

            docs = vectorstore.similarity_search(test_case, k=2)
            doc_context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        You are a Senior QA Automation Engineer.
        
        TASK:
        Write a Python Selenium script for this specific Test Case.
        
        TEST CASE:
        "{test_case}"
        
        RELEVANT DOCUMENTATION (Logic/Rules):
        {doc_context}
        
        TARGET HTML SOURCE (For IDs/Selectors):
        ```html
        {html_code}
        ```
        
        STRICT REQUIREMENTS:
        1. Use 'webdriver.Chrome()'.
        2. Assume 'checkout.html' is in the local folder: driver.get("file:///absolute/path/to/checkout.html") (Use os.getcwd + checkout.html).
        3. Use the Logic from Documentation (e.g., if doc says code is SAVE15, use SAVE15).
        4. Use IDs/Classes from the provided HTML.
        5. Add assertions to verify the Expected Result.
        6. Return ONLY the Python code block.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt
        )
        
        return response.text

    except Exception as e:
        return f"Error generating script: {str(e)}"