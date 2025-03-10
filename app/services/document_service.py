from config import db
from google.cloud import firestore

def add_document(content: str):
    document_data = {
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    doc_ref = db.collection("documents").document()
    doc_ref.set(document_data)

    return {"id": doc_ref.id, "content": content}
    
def doc_by_id(document_id: str):
        doc_ref = db.collection("documents").document(document_id)
        doc = doc_ref.get()
        return {"id": doc.id,**doc.to_dict()}
    
def limit_docs(skip: int = 0, limit: int = 10):
    try:
        docs = db.collection("documents").offset(skip).limit(limit).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        return {"error": str(e)}