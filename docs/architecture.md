# Ruzivo — System Architecture

## Components

| Component | Technology | Status |
|-----------|-----------|--------|
| LLM | Mistral 7B + QLoRA (Shona fine-tune) | Planned (Phase 3–5) |
| ASR | Whisper small (Shona fine-tune) | Planned (Phase 6–8) |
| TTS | Coqui TTS (Shona voice) | Planned (Phase 9–10) |
| Backend API | FastAPI + PostgreSQL + Redis | Scaffold done |
| Frontend | React Native (Expo) | Planned (Phase 12) |
| RAG | ChromaDB + sentence-transformers | Planned (Phase 13) |
| Data Pipeline | Scrapy + pandas | Phase 2 in progress |

## Data Flow

User voice input → Whisper ASR → Shona text
Shona text + RAG context → Mistral 7B → Shona response text
Shona response text → Coqui TTS → Audio output

Image upload → LLaVA description (English) → Mistral 7B → Shona response
Document upload → text extraction → Mistral 7B context → Shona response
