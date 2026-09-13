from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import Base, engine
from app.routers import chat, asr, tts, files, auth
from app.services.tts import tts_service
from app.services.rag import rag_service
from app.services.llm import llm_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    rag_service.load()
    tts_service.load()
    llm_service.load()
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(asr.router)
app.include_router(tts.router)
app.include_router(files.router)

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
