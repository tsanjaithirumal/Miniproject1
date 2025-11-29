from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app import models, database, auth, rag_engine
from typing import List, Optional
import shutil
import os
import uuid
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class DocumentResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    category: Optional[str]
    description: Optional[str]
    metadata_info: Optional[str]

    class Config:
        orm_mode = True

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(None),
    description: str = Form(None),
    metadata_info: str = Form(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Validate file size (approx 16MB limit check would be better done via middleware or reading chunks, 
    # but for simplicity we'll assume the server config handles max body size, or we check after read)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".png", ".jpg", ".jpeg", ".txt"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Secure filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    db_doc = models.Document(
        user_id=current_user.id,
        filename=file.filename, # Original name
        file_path=file_path,
        category=category,
        description=description,
        metadata_info=metadata_info
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # Trigger RAG processing (async in production, sync here for simplicity)
    try:
        rag_engine.process_document(db_doc.id, file_path, db)
    except Exception as e:
        print(f"Error processing document: {e}")
        # We don't fail the upload if indexing fails, but we should log it

    return db_doc

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return db.query(models.Document).filter(models.Document.user_id == current_user.id).all()

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    doc = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    # Remove from DB
    db.delete(doc)
    db.commit()
    
    # Remove from Vector Store
    rag_engine.delete_document_embeddings(doc.id)

    return {"message": "Document deleted"}
