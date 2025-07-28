import os
import shutil
from huggingface_hub import hf_hub_download

models_dir = r"models"
os.makedirs(models_dir, exist_ok=True)

from huggingface_hub import snapshot_download

model_path = snapshot_download(repo_id="BAAI/bge-small-en", local_dir=f"{models_dir}/bge-small-en", local_dir_use_symlinks=False)

# Download phi‑1.5 Q4_0 GGUF
phi_repo = "tensorblock/phi-1_5-GGUF"
phi_filename = "phi-1_5-Q4_0.gguf"
print("📥 Downloading phi‑1.5 Q4_0 GGUF from tensorblock...")
phi_path = hf_hub_download(repo_id=phi_repo, filename=phi_filename)
shutil.copy(phi_path, os.path.join(models_dir, "phi-1.5.Q4_0.gguf"))
print("✅ phi‑1.5.Q4_0.gguf downloaded to:", models_dir)
