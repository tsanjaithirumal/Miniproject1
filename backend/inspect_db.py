import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# Same setup as rag_engine.py
CHROMA_DB_DIR = "chroma_db"
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

class LocalEmbeddingFunction(chromadb.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        return embedding_model.encode(input).tolist()

try:
    collection = client.get_collection(
        name="medical_docs",
        embedding_function=LocalEmbeddingFunction()
    )
    print(f"Collection 'medical_docs' found.")
    print(f"Total items in collection: {collection.count()}")
    
    if collection.count() > 0:
        print("Peeking at first 2 items:")
        print(collection.peek(limit=2))
    else:
        print("Collection is empty! Documents are not being indexed.")

except Exception as e:
    print(f"Error accessing collection: {e}")
