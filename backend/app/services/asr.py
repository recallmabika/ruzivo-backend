import torch
import soundfile as sf
import tempfile
import os
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from app.config import settings

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class ASRService:
    def __init__(self):
        self.model = None
        self.processor = None

    def load(self):
        self.processor = WhisperProcessor.from_pretrained(
            "openai/whisper-small",
            language="shona",
            task="transcribe"
        )
        self.model = WhisperForConditionalGeneration.from_pretrained(
            settings.ASR_MODEL_ID,
            token=settings.HF_TOKEN
        ).to(DEVICE)
        self.model.config.forced_decoder_ids = None
        self.model.config.suppress_tokens = []
        self.model.eval()

    def transcribe(self, audio_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            audio, sr = sf.read(tmp_path)
            if sr != 16000:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            inputs = self.processor.feature_extractor(
                audio, sampling_rate=16000, return_tensors="pt"
            ).to(DEVICE)
            with torch.no_grad():
                predicted_ids = self.model.generate(inputs.input_features)
            transcript = self.processor.tokenizer.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]
            return transcript
        finally:
            os.unlink(tmp_path)

asr_service = ASRService()
