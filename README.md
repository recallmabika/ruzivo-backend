# Ruzivo — Multimodal Conversational Shona AI System

BSc Honours Computer Science Dissertation Project  
Recall T. Mabika | R247360N | Midlands State University

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/recallmabika/ruzivo.git
cd ruzivo
make setup

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Start backend
make run-backend

# 4. Run data pipeline (Phase 2)
make run-pipeline
```

## Project Structure

```
ruzivo/
├── backend/          # FastAPI REST API
├── frontend/         # React Native (Expo) mobile app
├── pipeline/         # Scrapy corpus + audio data collection
├── models/           # Fine-tuning scripts (LLM, ASR, TTS)
├── rag/              # ChromaDB knowledge base
├── notebooks/        # Colab/Kaggle training notebooks
├── infra/docker/     # Docker Compose
└── data/             # Raw and processed corpora
```

## Development Phases

- [x] Phase 1: Literature review & project scaffold
- [ ] Phase 2: Shona text corpus (Scrapy)
- [ ] Phase 3: Corpus cleaning & preparation
- [ ] Phase 4–5: Mistral 7B QLoRA fine-tuning
- [ ] Phase 6–8: Whisper ASR fine-tuning
- [ ] Phase 9–10: Coqui TTS voice training
- [ ] Phase 11: FastAPI backend
- [ ] Phase 12: React Native frontend
- [ ] Phase 13: RAG pipeline
- [ ] Phase 14: Integration & testing
- [ ] Phase 15: Dissertation write-up
