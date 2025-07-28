import os
import shutil
from huggingface_hub import hf_hub_download

models_dir = r"models"
os.makedirs(models_dir, exist_ok=True)

# Download bge‑small‑en files
bge_dir = os.path.join(models_dir, "bge-small-en")
os.makedirs(bge_dir, exist_ok=True)

bge_files = [
    "config.json",
    "pytorch_model.bin",
    "sentence_bert_config.json",
    "tokenizer_config.json",
    "vocab.txt",
]

print("📥 Downloading BGE‑small‑en...")
for fname in bge_files:
    path = hf_hub_download(repo_id="BAAI/bge-small-en", filename=fname)
    shutil.copy(path, os.path.join(bge_dir, fname))
print("✅ BGE‑small‑en downloaded to:", bge_dir)

# Download phi‑1.5 Q4_0 GGUF
phi_repo = "tensorblock/phi-1_5-GGUF"
phi_filename = "phi-1_5-Q4_0.gguf"
print("📥 Downloading phi‑1.5 Q4_0 GGUF from tensorblock...")
phi_path = hf_hub_download(repo_id=phi_repo, filename=phi_filename)
shutil.copy(phi_path, os.path.join(models_dir, "phi-1.5.Q4_0.gguf"))
print("✅ phi‑1.5.Q4_0.gguf downloaded to:", models_dir)
