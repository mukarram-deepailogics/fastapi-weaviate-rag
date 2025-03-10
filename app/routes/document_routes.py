from fastapi import APIRouter, HTTPException, Query
from app.models.document_model import Document
from app.services.document_service import add_document,doc_by_id,limit_docs

router = APIRouter()

@router.post("/documents", status_code=201)
async def create_document(document: Document):
    try:
        created_doc = add_document(document.content)
        return created_doc
    except  Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to add Document: {str(e)}")
    
@router.get("/document/{id}")
async def get_document(id:str):
    try:
        find = doc_by_id(id)
        return find
    except:
        raise HTTPException(status_code=404, detail="ID doesn't exists.")

@router.get("/documents/")
async def list_documents(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    list = limit_docs(skip, limit)
    if "error" in list:
        raise HTTPException(status_code=500, detail=list["error"])
    return list