from fastapi import APIRouter, HTTPException
from app.models.question_model import QueryWeaviateRequest
from app.services.weaviate_query_service import query_weaviate
from app.services.llm_service import call_llm

router = APIRouter()

@router.post("/query_weaviate")
async def query_weaviate_endpoint(request: QueryWeaviateRequest):
    try:
        # 🔹 Ensure document_id is None if it's empty or a placeholder
        document_id = request.document_id if request.document_id and request.document_id != "string" else None

        results = query_weaviate(request.question, document_id)

        if not results:
            return empty_response()  # ✅ Return empty JSON if no results found

        context_data = process_results(results)

        # 🔹 If no meaningful context is found, return an empty response
        if not context_data["context"].strip():
            return empty_response()

        prompt = format_prompt(context_data["context"], request.question)
        answer = call_llm(prompt)

        # 🔹 If LLM says "I don't know", return an empty response
        if answer.strip().lower() == "i don't know.":
            return empty_response()

        return {
            "answer": answer,
            "context": context_data["chunks"],
            "document_id": context_data["document_ids"],
            "page_number": context_data["page_numbers"],
            "certainty": context_data["avg_certainty"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_results(results):
    """Extract and format data from Weaviate results"""
    chunks, certainties, doc_ids, page_numbers = [], [], set(), set()

    for obj in results:
        chunks.append(obj["content"])
        certainties.append(obj["certainty"])
        doc_ids.add(obj["document_id"])
        page_numbers.add(obj["page_number"])

    return {
        "chunks": chunks,
        "avg_certainty": sum(certainties) / len(certainties) if certainties else 0,
        "document_ids": list(doc_ids),
        "page_numbers": list(page_numbers),
        "context": "\n\n".join(chunks)
    }

def format_prompt(context: str, question: str) -> str:
    return f"""Context information:
{context}

Question: {question}
Answer the question using only the context above. If unsure, say "I don't know".
Answer:"""

def empty_response():
    return {"No relevant information found in the documents."}  # ✅ Now properly returns an empty JSON object
