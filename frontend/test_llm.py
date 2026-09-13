from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

BASE_MODEL = "Qwen/Qwen2.5-1.5B"
ADAPTER_PATH = "./ruzivo-llm-v2"

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)

base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.float16, device_map="cpu")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

prompt = "### Instruction:\nTsanangura izvi muShona.\n\n### Response:\n"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=80, do_sample=True, temperature=0.7, top_p=0.9, pad_token_id=tokenizer.eos_token_id)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
