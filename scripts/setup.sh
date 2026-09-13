#!/usr/bin/env bash
set -e

echo ""
echo "  ██████╗ ██╗   ██╗███████╗██╗██╗   ██╗ ██████╗ "
echo "  ██╔══██╗██║   ██║╚══███╔╝██║██║   ██║██╔═══██╗"
echo "  ██████╔╝██║   ██║  ███╔╝ ██║██║   ██║██║   ██║"
echo "  ██╔══██╗██║   ██║ ███╔╝  ██║╚██╗ ██╔╝██║   ██║"
echo "  ██║  ██║╚██████╔╝███████╗██║ ╚████╔╝ ╚██████╔╝"
echo "  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═════╝ "
echo ""
echo "  Ruzivo — Shona AI System — Project Setup"
echo ""

# Python version check
PYTHON=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON | cut -d. -f1)
MINOR=$(echo $PYTHON | cut -d. -f2)
if [ "$MAJOR" -lt 3 ] || [ "$MINOR" -lt 11 ]; then
  echo "  ❌ Python 3.11+ required. Found: $PYTHON"
  exit 1
fi
echo "  ✅ Python $PYTHON"
# Virtual environment
if [ ! -d ".venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
# Upgrade pip
pip install --upgrade pip --quiet
# Pre-install openai-whisper separately — its legacy setup.py breaks
# under pip's build isolation on Python 3.11 (pkg_resources not found).
echo "  Pre-installing openai-whisper (legacy build workaround)..."
pip install openai-whisper --no-build-isolation --quiet
 
# Install dependencies
echo "  Installing backend dependencies..."
pip install -r backend/requirements.txt --quiet
echo "  Installing pipeline dependencies..."
pip install -r pipeline/requirements.txt --quiet
# Copy .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  ✅ .env created from .env.example — update your secrets before running"
fi
# Create data dirs
mkdir -p data/raw/text data/raw/audio
mkdir -p data/processed/text data/processed/audio
echo ""
echo "  ✅ Setup complete!"
echo ""
echo "  Next steps:"
echo "    source .venv/bin/activate"
echo "    make run-backend 
echo "    make run-pipeline
echo ""