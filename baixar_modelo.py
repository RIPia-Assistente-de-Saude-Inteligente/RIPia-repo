from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen2.5-0.5B-Instruct",
    local_dir="./hf/qwen-0.5b",
    resume_download=True,
    max_workers=1  # Reduz carga de download simultâneo
)