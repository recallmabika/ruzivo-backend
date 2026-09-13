from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import fitz  # pymupdf
from docx import Document
import io

router = APIRouter(prefix="/files", tags=["files"])

class FileResponse(BaseModel):
    text: str
    filename: str
    file_type: str

@router.post("/extract", response_model=FileResponse)
async def extract_text(file: UploadFile = File(...)):
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large — max 10MB")
    content = await file.read()
    text = ""
    if file.content_type == "application/pdf":
        pdf = fitz.open(stream=content, filetype="pdf")
        text = "\n".join([page.get_text() for page in pdf])
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    elif file.content_type == "text/plain":
        text = content.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from file")
    return FileResponse(
        text=text[:50000],
        filename=file.filename,
        file_type=file.content_type
    )
