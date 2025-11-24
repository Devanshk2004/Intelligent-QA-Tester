import os
from dotenv import load_dotenv
from google import genai 
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv() 

MODEL_NAME = "gemini-2.5-flash" 

def ask_bot(query):
    try:
        client = genai.Client()

        if not os.path.exists("chroma_db"):
            return "Knowledge Base not found. Please build it first."

        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embedding_model)
        
        docs = vectorstore.similarity_search(query, k=3)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        full_prompt = f"""You are an expert QA Automation Engineer.
        Your task is to generate comprehensive Test Cases based STRICTLY on the provided context.

        GUIDELINES:
        1. Use ONLY the provided context. Do not invent features.
        2. Format the output as a Markdown Table.
        3. The table MUST have these columns: Test_ID, Feature, Test_Scenario, Expected_Result, Grounded_In.
        4. 'Grounded_In' column must cite the specific document name (e.g., product_specs.md).

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