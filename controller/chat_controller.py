from flask import Blueprint, request, jsonify, session, current_app
from controller.agendamento_controller import agendar

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].strip().lower()
    model_ready = current_app.config.get('model_ready', False)
    model = current_app.config.get('model', None)
    tokenizer = current_app.config.get('tokenizer', None)

    # Se o usuário ainda não iniciou o chat
    if 'step' not in session:
        session['step'] = 'menu_principal'

    step = session['step']

    # Menu principal
    if step == 'menu_principal':
        if user_message in ['marcar consulta']:
            session['step'] = 'agendamento'
            session['step_agendamento'] = 0
            session['dados'] = {}
            return jsonify({
                'response': 'Vamos iniciar o agendamento. Digite seu nome:',
                'options': ['Sair']
            })

        elif user_message in ['informações sobre serviços']:
            session['step'] = 'servicos'
            return jsonify({
                'response': 'Escolha um serviço para saber mais:',
                'options': ['Consulta Clínica', 'Exames Laboratoriais', 'Voltar']
            })

        elif user_message in ['perguntas sobre saúde']:
            session['step'] = 'perguntas_saude'
            return jsonify({'response': 'Digite sua pergunta de saúde ou "voltar" para sair da IA.'})

        elif user_message in ['sair']:
            session.clear()
            return jsonify({'response': 'Encerrando o atendimento. Até logo!'})

        else:
            return jsonify({
                'response': 'Escolha uma opção válida:',
                'options': ['Marcar consulta', 'Informações sobre serviços', 'Perguntas sobre saúde', 'Sair']
            })

    # Fluxo de Agendamento (usando o controller que você já tem)
    if step == 'agendamento':
        if user_message == 'sair':
            session.clear()
            return jsonify({'response': 'Agendamento cancelado.', 'options': ['Voltar ao Menu Principal']})
        return agendar()

    # Fluxo de Serviços
    if step == 'servicos':
        if user_message == 'consulta clínica':
            return jsonify({
                'response': 'Consultas de clínica geral de segunda a sexta, das 8h às 18h.',
                'options': ['Voltar']
            })
        elif user_message == 'exames laboratoriais':
            return jsonify({
                'response': 'Realizamos hemograma, glicemia e outros exames. Atendimento das 7h às 17h.',
                'options': ['Voltar']
            })
        elif user_message == 'voltar':
            session['step'] = 'menu_principal'
            return jsonify({
                'response': 'Voltando ao menu principal.',
                'options': ['Marcar consulta', 'Informações sobre serviços', 'Perguntas sobre saúde', 'Sair']
            })
        else:
            return jsonify({'response': 'Escolha uma opção válida:', 'options': ['Consulta Clínica', 'Exames Laboratoriais', 'Voltar']})

    # Fluxo de Perguntas de Saúde (único que usa a LLM)
    if step == 'perguntas_saude':
        if user_message == 'voltar':
            session['step'] = 'menu_principal'
            return jsonify({
                'response': 'Voltando ao menu principal.',
                'options': ['Marcar consulta', 'Informações sobre serviços', 'Perguntas sobre saúde', 'Sair']
            })

        if not model_ready:
            return jsonify({'response': 'Aguarde... IA ainda carregando.'})

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é RIPia, um assistente de saúde. Responda sempre de forma breve, clara e em português. "
                    "Nunca faça diagnósticos ou prescreva tratamentos. Baseie-se apenas em informações amplamente reconhecidas. "
                    "Se não puder responder, oriente o usuário a buscar um profissional de saúde."
                )
            },
            {"role": "user", "content": user_message}
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(**model_inputs, max_new_tokens=512)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return jsonify({'response': response, 'options': ['Voltar ao Menu Principal']})

    # Fallback
    session.clear()
    return jsonify({'response': 'Fluxo inválido. Reiniciando o chat.', 'options': ['Marcar consulta', 'Informações sobre serviços', 'Perguntas sobre saúde', 'Sair']})

