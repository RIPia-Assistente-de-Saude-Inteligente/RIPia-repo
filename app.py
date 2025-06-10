import threading
from flask import Flask, render_template, jsonify
from controller.agendamento_controller import agendamento_bp
from controller.chat_controller import chat_bp
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
app.secret_key = 'secret_key_for_session_management'

model_ready = False
model = None
tokenizer = None

def load_model():
    global model, tokenizer, model_ready
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_ready = True
    # Store in app config for blueprint access
    app.config['model'] = model
    app.config['tokenizer'] = tokenizer
    app.config['model_ready'] = model_ready

threading.Thread(target=load_model).start()

@app.route('/')
def index():
    return render_template('chat.html' if model_ready else 'loading.html')

@app.route('/loading')
def loading_status():
    return jsonify({'model_ready': model_ready})

# Registra os blueprints
app.register_blueprint(agendamento_bp)
app.register_blueprint(chat_bp)

if __name__ == '__main__':
    app.run(debug=True)