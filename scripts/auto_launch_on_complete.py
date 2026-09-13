import os
import sys
import time
import subprocess
from pathlib import Path

target_file = Path.home() / ".cache" / "huggingface" / "hub" / "model.safetensors"
EXPECTED_SIZE = 3080000000  # ~3.08 GB

print("Monitoring download until completion...")
while True:
    if target_file.exists():
        size = target_file.stat().st_size
        mb = size / (1024 * 1024)
        pct = (size / EXPECTED_SIZE) * 100
        if size >= 3050000000:
            print(f"Download complete: {mb:.2f} MB!")
            break
    time.sleep(30)

print("Now launching run_real_server.py...")
subprocess.run([sys.executable, "scripts/run_real_server.py"], cwd=r"c:\Users\recal\Desktop\Level 2.2 Project\ruzivo")
