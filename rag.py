import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def load_and_index(uploaded_file, gemini_api_key):
    file_name = uploaded_file.name
    temp_path = f"temp_{file_name}"

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    if file_name.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
    elif file_name.endswith(".txt"):
        loader = TextLoader(temp_path)
    else:
        os.remove(temp_path)
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
    
    documents = loader.load()
    os.remove(temp_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
        )
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model = "models/embedding-001",
        google_api_key = gemini_api_key
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
        )
    return vector_store

def search_document(vector_store, query, threshold= 0.55):
    results = vector_store.similarity_search_with_score(query, k=1)
    best_doc, score = results[0]

    if score < threshold:
        return best_doc.page_content, True
    else:
        return "No relevant information found in the document.", False