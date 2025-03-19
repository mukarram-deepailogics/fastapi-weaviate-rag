from fastapi import APIRouter, HTTPException
from app.models.question_model import QueryWeaviateRequest
from app.services.weaviate_query_service import query_weaviate, WeaviateConnectionError, NoResultsFoundError
from app.services.llm_service import call_llm

router = APIRouter()

@router.post("/query_weaviate")
async def query_weaviate_endpoint(request: QueryWeaviateRequest):
    try:
        document_id = request.document_id if request.document_id and request.document_id != "string" else None

        try:
            results = query_weaviate(request.question, document_id)
        except WeaviateConnectionError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except NoResultsFoundError:
            return no_document_found_response(document_id)  # ✅ Return "No document with the given ID found"

        context_data = process_results(results)

        if not context_data["chunks"]:  # ✅ If no valid content, return "I don't know."
            return empty_response()

        prompt = format_prompt(context_data["context"], request.question)

        try:
            answer = call_llm(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

        # ✅ If LLM says "I don't know.", return only that.
        if answer.strip().lower() == "i don't know.":
            return empty_response()

        return {
            "answer": answer,
            "context": context_data["chunks"],
            "document_id": context_data["document_ids"],
            "page_number": context_data["page_numbers"],
            "certainty": context_data["avg_certainty"]
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def process_results(results):
    """Process Weaviate results into structured data"""
    chunks, certainties, doc_ids, page_numbers = [], [], set(), set()

    for obj in results:
        content = obj.get("content", "").strip()
        if content:
            chunks.append(content)
            certainties.append(obj.get("certainty", 0))
            doc_ids.add(obj.get("document_id", ""))
            page_numbers.add(obj.get("page_number", 0))

    return {
        "chunks": chunks,
        "avg_certainty": sum(certainties) / len(certainties) if certainties else 0,
        "document_ids": list(doc_ids),
        "page_numbers": list(page_numbers),
        "context": "\n\n".join(chunks)
    }

def format_prompt(context: str, question: str) -> str:
    """Formats the LLM prompt with given context and question"""
    return f"""Context information:
{context}

Question: {question}
Answer the question using only the context above. If unsure, say "I don't know".
Answer:"""

def empty_response():
    """✅ Ensures ONLY 'I don't know.' is returned"""
    return {"answer": "I don't know."}

def no_document_found_response(document_id):
    """✅ Returns a proper response when an invalid document ID is given"""
    return {"answer": "No document with the given ID was found."}
