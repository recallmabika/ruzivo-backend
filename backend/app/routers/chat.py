from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.llm import llm_service
from app.services.rag import rag_service
from app.utils.language import is_shona, SHONA_ONLY_RESPONSE

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: str | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str | None = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not is_shona(request.message):
        return ChatResponse(response=SHONA_ONLY_RESPONSE)

    rag_context = rag_service.retrieve(request.message)
    combined_context = request.context or ""
    if rag_context:
        combined_context += f"\n{rag_context}"

    response = llm_service.generate(
        instruction=request.message,
        context=combined_context.strip()
    )

    return ChatResponse(response=response, conversation_id=request.conversation_id)
