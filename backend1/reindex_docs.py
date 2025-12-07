from app import models, database, rag_engine
import os

db = database.SessionLocal()
docs = db.query(models.Document).all()

print(f"Found {len(docs)} documents in database.")

for doc in docs:
    print(f"Re-indexing Document ID: {doc.id}, Filename: {doc.filename}")
    # Check if file exists
    if os.path.exists(doc.file_path):
        try:
            rag_engine.process_document(doc.id, doc.file_path, db)
        except Exception as e:
            print(f"Error processing {doc.filename}: {e}")
    else:
        print(f"File missing: {doc.file_path}")

print("Re-indexing complete.")
