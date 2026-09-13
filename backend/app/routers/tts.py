from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.services.tts import tts_service

router = APIRouter(prefix="/tts", tags=["tts"])

class TTSRequest(BaseModel):
    text: str

@router.post("/synthesize")
async def synthesize(request: TTSRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text required")
    if len(request.text) > 500:
        raise HTTPException(status_code=400, detail="Text too long — max 500 characters")
    audio_bytes = tts_service.synthesize(request.text)
    return Response(content=audio_bytes, media_type="audio/wav")
