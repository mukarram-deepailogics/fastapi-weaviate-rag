from fastapi import FastAPI
from config import db
from app.routes import document_routes

app = FastAPI()

app.include_router(document_routes.router)

#@app.get("/testing-firestore")
#def test_firestore():
#    doc_ref = db.collection("test").document("dummy")
#    doc_ref.set({"content": "This is a test document"})
#    doc = doc_ref.get()
#    return {"id": doc.id, "data": doc.to_dict()}

@app.get("/")
async def root():
    return {"message": "welcome"}