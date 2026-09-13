from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BASE_MODEL = "Qwen/Qwen2.5-1.5B"

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.float16, device_map="cpu")
model.eval()

prompt = "Mhoro, makadii?"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=40, do_sample=False, pad_token_id=tokenizer.eos_token_id)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
