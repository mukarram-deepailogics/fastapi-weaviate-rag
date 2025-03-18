# app/models/question_model.py
from pydantic import BaseModel

class QueryWeaviateRequest(BaseModel):
    question: str
    document_id: str = None