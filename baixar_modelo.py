import os
from huggingface_hub import snapshot_download

local_dir = "./hf/qwen-0.5b"

# Só baixa se a pasta ainda não existir
if not os.path.exists(local_dir):
    snapshot_download(
        repo_id="Qwen/Qwen2.5-0.5B-Instruct",
        local_dir=local_dir,
        resume_download=True,
        max_workers=1
    )
    print("📥 Modelo baixado com sucesso.")
else:
    print("✅ Modelo já existe. Download ignorado.")
