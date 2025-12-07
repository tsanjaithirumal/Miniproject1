import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import pytesseract
from PIL import Image
from sqlalchemy.orm import Session
from app import models

# Initialize ChromaDB
# Persist data to disk
CHROMA_DB_DIR = "chroma_db"
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

# Use a local model for embeddings to ensure privacy and no cost
# 'all-MiniLM-L6-v2' is a good balance of speed and quality
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Custom embedding function for Chroma
class LocalEmbeddingFunction(chromadb.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        return embedding_model.encode(input).tolist()

collection = client.get_or_create_collection(
    name="medical_docs",
    embedding_function=LocalEmbeddingFunction()
)

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Tesseract Path Configuration for Windows
# Attempt to find tesseract binary in common locations
tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.join(os.getenv('LOCALAPPDATA', ''), r"Tesseract-OCR\tesseract.exe"),
    os.path.join(os.getenv('LOCALAPPDATA', ''), r"Programs\Tesseract-OCR\tesseract.exe"),
    r"C:\Tesseract-OCR\tesseract.exe"
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"Found Tesseract at: {path}")
        break

def extract_text_from_image(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found. Please install Tesseract-OCR.")
        return "[Image content cannot be read - Tesseract OCR is not installed on the server]"
    except Exception as e:
        print(f"OCR Error: {e}")
        return f"[Error extracting text from image: {str(e)}]"

def process_document(doc_id: int, file_path: str, db: Session):
    """
    Extracts text, chunks it, and stores embeddings in ChromaDB.
    """
    print(f"[RAG Debug] Processing document {doc_id} path: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[RAG Debug] File not found: {file_path}")
        return

    file_ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if file_ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)
    elif file_ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
    print(f"[RAG Debug] Extracted {len(text)} characters.")
            
    if not text.strip():
        print("[RAG Debug] Text is empty. Indexing metadata only.")
        text = f"Filename: {os.path.basename(file_path)}\n"
        # We can't easily get description here without DB query, but we can at least index the filename
        # so the user knows the file exists but is unreadable.
        text += "[Content unreadable - Scanned document or Image without OCR]"

    # Simple chunking strategy
    chunk_size = 1000
    overlap = 100
    chunks = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        
    if not chunks:
        return

    # Add to ChromaDB
    # We store doc_id in metadata to filter by user/document later
    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id} for _ in chunks]
    
    print(f"[RAG Debug] Indexing document {doc_id} ({file_path})...")
    print(f"[RAG Debug] Created {len(chunks)} chunks.")

    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    print(f"[RAG Debug] Successfully added to ChromaDB.")

def delete_document_embeddings(doc_id: int):
    """
    Removes all chunks related to a document from ChromaDB.
    """
    collection.delete(
        where={"doc_id": doc_id}
    )

def query_rag(query_text: str, user_id: int, db: Session, n_results: int = 3) -> str:
    """
    Retrieves relevant context and generates an answer.
    """
    # 1. Retrieve relevant chunks for this user
    # We need to get all doc_ids belonging to the user first to filter
    user_docs = db.query(models.Document).filter(models.Document.user_id == user_id).all()
    user_doc_ids = [doc.id for doc in user_docs]
    
    print(f"[RAG Debug] User {user_id} has documents: {user_doc_ids}")

    if not user_doc_ids:
        print("[RAG Debug] No documents found for user.")
        return "You haven't uploaded any documents yet."

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"doc_id": {"$in": user_doc_ids}} # Filter by user's documents
    )
    
    print(f"[RAG Debug] Query: {query_text}")
    print(f"[RAG Debug] Retrieved {len(results['documents'][0])} chunks")
    # print(f"[RAG Debug] Chunks: {results['documents'][0]}") # Uncomment for verbose output
    
    context_chunks = results['documents'][0]
    context = "\n\n".join(context_chunks)
    
    # 2. Generate Answer with Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "paste_your_key_here":
        return "[System] Gemini API Key is missing. Please add it to backend/.env file."

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        You are a helpful medical assistant. 
        - If the user's input is a greeting (like "Hi", "Hello") or general conversation, respond politely and ask how you can help with their medical records.
        - For specific questions, answer based ONLY on the provided context.
        - If the answer to a specific question is not in the context, say "I cannot find this information in your documents."
        
        Context:
        {context}
        
        Question:
        {query_text}
        
        Answer:
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Error] Failed to generate response from Gemini: {str(e)}"
