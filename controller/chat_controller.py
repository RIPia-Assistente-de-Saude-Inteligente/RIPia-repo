from flask import Blueprint, request, jsonify, session, current_app

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    model_ready = current_app.config.get('model_ready', False)
    model = current_app.config.get('model', None)
    tokenizer = current_app.config.get('tokenizer', None)

    if not model_ready:
        return jsonify({'error': 'Model is still loading!'}), 503
    user_message = request.json['message'].strip().lower()

    if user_message in ["marcar consulta", "agendar", "agendar consulta"]:
        session['step'] = 0
        session['dados'] = {}
        return jsonify({'response': "Digite seu nome:"})

    if 'step' in session:
        from controller.agendamento_controller import agendar
        return agendar()

    else:
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é RIPia, um assistente automático de saúde baseado no modelo Qwen. "
                    "Responda sempre em português, de forma clara, objetiva e educada. "
                    "Sua função é fornecer informações gerais de saúde, sem nunca prescrever medicamentos, indicar tratamentos específicos ou realizar diagnósticos. "
                    "Baseie todas as respostas apenas em informações confiáveis, amplamente reconhecidas e nunca invente dados, procedimentos ou resultados. "
                    "Se a dúvida do usuário exigir análise médica, tratamento personalizado ou diagnóstico, oriente-o a procurar um profissional de saúde qualificado. "
                    "Nunca faça afirmações categóricas ou promessas de cura. Quando não tiver certeza, diga claramente que não pode responder com precisão. "
                    "Jamais fuja do papel de assistente de saúde e nunca responda perguntas fora desse contexto."
                )
            },
            {"role": "user", "content": user_message}
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(**model_inputs, max_new_tokens=512)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in
                         zip(model_inputs.input_ids, generated_ids)]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return jsonify({'response': response})