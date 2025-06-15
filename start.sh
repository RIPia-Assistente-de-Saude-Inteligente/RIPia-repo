#!/bin/bash

# Nome da venv
VENV_DIR="venv"

# Cria a venv se não existir
if [ ! -d "$VENV_DIR" ]; then
    echo "Criando virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Ativa a venv
source "$VENV_DIR/bin/activate"

# Instala as dependências (só se não estiverem instaladas)
echo "Instalando dependências..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install flask transformers accelerate huggingface_hub
pip install sqlalchemy
# baixa o modelo do Hugging Face
echo "Baixando modelo do Hugging Face..."
python baixar_modelo.py
#git clone https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
# deletar cache do Hugging Face do pc
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct
# Roda o app
echo "Iniciando aplicação..."
python app.py

