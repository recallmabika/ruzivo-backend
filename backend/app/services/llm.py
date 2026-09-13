from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

BASE_MODEL = "Qwen/Qwen2.5-1.5B"
ADAPTER_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "ruzivo-llm-v6"


class LLMService:
    def __init__(self):
        self._tokenizer = None
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        self._tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_PATH))
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, dtype=torch.float16, device_map="cpu"
        )
        self._model = PeftModel.from_pretrained(base_model, str(ADAPTER_PATH))
        self._model.eval()

    def load(self):
        # public entry point called by lifespan in main.py
        self._load()

    def generate(self, instruction: str, context: str = "", max_new_tokens: int = 120) -> str:
        self._load()

        system_message = (
            "Iwe uri Ruzivo, mubatsiri wehungwaru wekunyora nekutaura muChiShona chete. "
            "Pindura mibvunzo zvizere uye nechokwadi. "
            "Kana paine mashoko akapihwa (Context), shandisa mashoko iwayo chete kupindura. "
            "Kana usingazivi mhinduro yacho, kana mashoko asipo muContext, taura pachena kuti 'Handizivi mhinduro yacho' pane kuedza kufungidzira."
        )

        if context:
            user_content = f"Tsanangudzo (Context):\n{context}\n\nMubvunzo:\n{instruction}"
        else:
            user_content = instruction

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]

        if hasattr(self._tokenizer, "apply_chat_template") and self._tokenizer.chat_template:
            prompt = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n"

        inputs = self._tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.3,  # lower temperature to suppress hallucination
                top_p=0.85,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        # Slice generated output beyond input prompt tokens
        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self._tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        if "<|im_end|>" in response:
            response = response.split("<|im_end|>")[0].strip()

        return response


llm_service = LLMService()