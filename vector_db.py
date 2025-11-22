import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader, JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import BSHTMLLoader

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

DB_DIR = "chroma_db"

def process_and_store_documents(uploaded_files):

    documents = []
    
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name

        loader = None
        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(temp_path)
            elif file_extension == ".md":
                loader = UnstructuredMarkdownLoader(temp_path)
            elif file_extension == ".txt":
                loader = TextLoader(temp_path, encoding="utf-8")
            elif file_extension == ".json":
                loader = TextLoader(temp_path, encoding="utf-8")
            elif file_extension == ".html":
                loader = BSHTMLLoader(temp_path) 

            if loader:
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_document"] = file.name
                documents.extend(docs)
        
        except Exception as e:
            print(f"Error processing {file.name}: {e}")
        
        finally:
            os.remove(temp_path)

    if not documents:
        return "No documents processed."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_model, 
        persist_directory=DB_DIR
    )
    
    return f"Success! Processed {len(documents)} documents into {len(chunks)} chunks."