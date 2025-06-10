from flask import Blueprint, request, jsonify, session
from models.db import especialidades, exames, horarios
from models.agendamento import process_agendamento
import re
from datetime import datetime

agendamento_bp = Blueprint('agendamento', __name__)

def validar_data(data_texto):
    try:
        datetime.strptime(data_texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_hora(hora_texto):
    return bool(re.match(r'^\d{2}:\d{2}$', hora_texto))

def listar_opcoes(collection):
    return "\n".join(f"- {item['nome']}" for item in collection.find({}, {"_id": 0, "nome": 1}))

@agendamento_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    return jsonify(list(especialidades.find({}, {"_id": 0, "nome": 1})))

@agendamento_bp.route('/exames', methods=['GET'])
def listar_exames():
    return jsonify(list(exames.find({}, {"_id": 0, "nome": 1})))

@agendamento_bp.route('/agendar', methods=['POST'])
def agendar():
    session.setdefault('step', 0)
    session.setdefault('dados', {})

    step = session['step']
    dados = session['dados']
    user_message = request.json['message'].strip()

    perguntas = [
        "Digite seu nome:",
        "Digite seu telefone:",
        "Digite seu e-mail:",
        "Digite a especialidade desejada:",
        "Digite o exame desejado (ou 'nenhum'):",
        "Digite a data do agendamento (DD/MM/AAAA):",
        "Digite o horário do agendamento (HH:MM):",
        "Confirma o agendamento? (sim/não)"
    ]

    campos = [
        "nome", "telefone", "email",
        "especialidade", "exame", "data",
        "hora", "confirmar"
    ]

    def validar_campo(campo, valor):
        if campo == "especialidade":
            if not especialidades.find_one({"nome": valor}):
                return f"Especialidade '{valor}' não encontrada.\nOpções:\n{listar_opcoes(especialidades)}"
        if campo == "exame":
            if valor.lower() != 'nenhum' and not exames.find_one({"nome": valor}):
                return f"Exame '{valor}' não encontrado.\nOpções:\n{listar_opcoes(exames)}\nOu digite 'nenhum'."
        if campo == "data":
            if not validar_data(valor):
                return "Data inválida. Informe no formato DD/MM/AAAA."
        if campo == "hora":
            if not validar_hora(valor):
                return "Horário inválido. Informe no formato HH:MM."
        if campo == "confirmar":
            if valor.lower() not in ['sim', 'não', 'nao']:
                return "Responda 'sim' para confirmar ou 'não' para cancelar."
        if campo == "telefone":
            if not re.fullmatch(r'\d{8,15}', valor):
                return "Telefone inválido. Informe apenas números, entre 8 e 15 dígitos."
        if campo == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", valor):
                return "E-mail inválido. Informe no formato exemplo@dominio.com."
        if campo == "nome":
            if len(valor.strip()) < 3:
                return "Nome muito curto. Informe seu nome completo."
        return None

    def obter_opcoes_para(campo):
        if campo == "especialidade":
            return f"\nOpções:\n{listar_opcoes(especialidades)}"
        if campo == "exame":
            return f"\nOpções:\n{listar_opcoes(exames)}\nOu digite 'nenhum'."
        if campo == "hora":
            # Exemplo de função fictícia para horários disponíveis
            especialidade = dados.get("especialidade")
            data = dados.get("data")
            if especialidade and data:
                horarios = horarios_disponiveis(especialidade, data)
                if horarios:
                    return f"\nHorários disponíveis para {especialidade} em {data}:\n" + ", ".join(horarios)
                else:
                    return "\nNenhum horário disponível para a data e especialidade escolhidas."
            else:
                return ""
        return ""

    # Função fictícia para exemplo. Implemente conforme sua lógica de negócio.
    def horarios_disponiveis(especialidade, data):
        resultados = horarios.find({
            "especialidade": especialidade,
            "data": data,
            "disponivel": True
        }, {"_id": 0, "hora": 1})
        return [item["hora"] for item in resultados]

    if step < len(campos) - 1:
        campo_atual = campos[step]
        erro = validar_campo(campo_atual, user_message)
        if erro:
            return jsonify({'response': erro})

        if campo_atual == "exame" and user_message.lower() == 'nenhum':
            dados[campo_atual] = None
        else:
            dados[campo_atual] = user_message

        session['step'] = step + 1
        session['dados'] = dados

        proxima_pergunta = perguntas[step + 1]
        opcoes = obter_opcoes_para(campos[step + 1])
        return jsonify({'response': f"{proxima_pergunta}{opcoes}"})

    elif step == len(campos) - 1:
        campo_atual = campos[step]
        erro = validar_campo(campo_atual, user_message)
        if erro:
            return jsonify({'response': erro})

        if user_message.lower() in ['sim']:
            resultado = process_agendamento(dados)
            print(f"Dados do agendamento: {dados}")
            print(f"Resultado do agendamento: {resultado}")
            resposta = resultado.get('mensagem', 'Erro ao realizar o agendamento.')
            if 'resumo' in resultado:
                resposta += f"\nResumo do agendamento:\n{resultado['resumo']}"
        else:
            resposta = "Agendamento cancelado."

        session.pop('step', None)
        session.pop('dados', None)

        return jsonify({'response': resposta})

    else:
        return jsonify({'response': "Ocorreu um erro no fluxo de agendamento. Por favor, reinicie."})