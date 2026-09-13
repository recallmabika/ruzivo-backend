from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.asr import asr_service

router = APIRouter(prefix="/asr", tags=["asr"])

class ASRResponse(BaseModel):
    transcript: str

@router.post("/transcribe", response_model=ASRResponse)
async def transcribe(audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Audio file required")
    audio_bytes = await audio.read()
    if len(audio_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large — max 10MB")
    transcript = asr_service.transcribe(audio_bytes)
    return ASRResponse(transcript=transcript)
