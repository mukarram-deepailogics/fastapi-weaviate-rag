from config import db
from google.cloud import firestore
from app.services.weaviate_db import insert_chunks_into_weaviate

def add_document(content: str):
    if not content:
        raise ValueError("Content is required.")

    document_data = {
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    
    doc_ref = db.collection("documents").document()
    doc_ref.set(document_data)

    document_id = doc_ref.id

    insert_chunks_into_weaviate(content, document_id, chunk_size=500, overlap=50)

    return {"id": document_id, "content": content}

def doc_by_id(document_id: str):
    doc_ref = db.collection("documents").document(document_id)
    doc = doc_ref.get()
    return {"id": doc.id, **doc.to_dict()}

def limit_docs(skip: int = 0, limit: int = 10):
    try:
        docs = db.collection("documents").offset(skip).limit(limit).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        return {"error": str(e)}
