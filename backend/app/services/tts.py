import torch
import numpy as np
import soundfile as sf
import io
from transformers import VitsModel, AutoTokenizer
from app.utils.language import is_shona, SHONA_ONLY_RESPONSE

class TTSService:
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-sna")
        self.model = VitsModel.from_pretrained("facebook/mms-tts-sna")
        self.model.eval()

    def synthesize(self, text: str) -> bytes:
        if not is_shona(text):
            text = SHONA_ONLY_RESPONSE
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = self.model(**inputs).waveform
        audio = output.squeeze().numpy()
        buffer = io.BytesIO()
        sf.write(buffer, audio, self.model.config.sampling_rate, format="WAV")
        buffer.seek(0)
        return buffer.read()

tts_service = TTSService()
