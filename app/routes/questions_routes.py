from fastapi import APIRouter, HTTPException
from app.services.openai_service import ask_openai
from app.models.question_model import QuestionRequest

router = APIRouter()

@router.post("/question")
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = ask_openai(request.question)
    return {"answer": answer}
