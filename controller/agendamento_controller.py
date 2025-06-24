from flask import Blueprint, request, jsonify, session
from models.db import Especialidade, Exame, Horario, engine
from models.agendamento import process_agendamento
from sqlalchemy.orm import Session
from sqlalchemy import func
import re
from datetime import datetime

agendamento_bp = Blueprint('agendamento', __name__)

import unicodedata

def remover_acentos(txt):
    return ''.join(
        c for c in unicodedata.normalize('NFD', txt)
        if unicodedata.category(c) != 'Mn'
    )

def validar_data(data_texto):
    try:
        datetime.strptime(data_texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_hora(hora_texto):
    return bool(re.match(r'^\d{2}:\d{2}$', hora_texto))

def listar_opcoes(modelo):
    with Session(engine) as db:
        return "\n".join(f"- {item.nome.title()}" for item in db.query(modelo).all())

def horarios_disponiveis(especialidade, data):
    with Session(engine) as db:
        resultados = db.query(Horario).filter(
            func.lower(Horario.especialidade) == especialidade.lower(),
            Horario.data == data,
            Horario.disponivel == True
        ).all()
        return [h.hora for h in resultados]

def datas_disponiveis(especialidade):
    with Session(engine) as db:
        resultados = db.query(Horario).filter(
            func.lower(Horario.especialidade) == especialidade.lower(),
            Horario.disponivel == True
        ).all()
        datas = sorted({h.data for h in resultados})
        try:
            return [datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") for d in datas]
        except:
            return datas

def obter_opcoes_para(campo, dados):
    if campo == "especialidade":
        return f"\nOpções:\n{listar_opcoes(Especialidade)}"

    if campo == "data":
        especialidade = dados.get("especialidade")
        if especialidade:
            datas = datas_disponiveis(especialidade)
            if datas:
                return f"\nDatas disponíveis para {especialidade.title()}:\n" + ", ".join(datas)
            else:
                return f"\nNenhuma data disponível para a especialidade {especialidade.title()}."
        else:
            return "\nEscolha uma especialidade primeiro."

    if campo == "hora":
        especialidade = dados.get("especialidade")
        data = dados.get("data")
        if especialidade and data:
            horarios_disp = horarios_disponiveis(especialidade, data)
            if horarios_disp:
                return f"\nHorários disponíveis para {especialidade.title()} em {data}:\n" + ", ".join(horarios_disp)
            else:
                return f"\nNenhum horário disponível para {especialidade.title()} em {data}."
        else:
            return "\nEscolha a especialidade e a data primeiro."

    if campo == "exame":
        return f"\nOpções:\n{listar_opcoes(Exame)}\nOu digite 'nenhum'."

    return ""

def validar_campo(campo, valor, dados):
    with Session(engine) as db:
        if valor.lower() == "sair":
            session.pop('step', None)
            session.pop('dados', None)
            return "Agendamento cancelado. Você saiu do processo."

        if campo == "especialidade":
            valor_normalizado = remover_acentos(valor.lower())
            especialidades = [remover_acentos(e.nome.lower()) for e in db.query(Especialidade).all()]
            if valor_normalizado not in especialidades:
                return f"Especialidade '{valor}' não encontrada.\nOpções:\n{listar_opcoes(Especialidade)}"

        if campo == "exame":
            if valor.lower() != 'nenhum' and not db.query(Exame).filter(func.lower(Exame.nome) == valor.lower()).first():
                return f"Exame '{valor}' não encontrado.\nOpções:\n{listar_opcoes(Exame)}\nOu digite 'nenhum'."

        if campo == "data":
            if not validar_data(valor):
                return "Data inválida. Informe no formato DD/MM/AAAA."

            especialidade = dados.get("especialidade")
            if especialidade:
                datas_disp = datas_disponiveis(especialidade)
                if valor not in datas_disp:
                    return f"A data '{valor}' não está disponível para a especialidade {especialidade.title()}.\n Informe uma das datas disponíveis: {', '.join(datas_disp)}"
            else:
                return "Você deve escolher uma especialidade antes da data."

        if campo == "hora":
            if not validar_hora(valor):
                return "Horário inválido. Informe no formato HH:MM."

            especialidade = dados.get("especialidade")
            data = dados.get("data")
            if especialidade and data:
                horarios_disp = horarios_disponiveis(especialidade, data)
                if valor not in horarios_disp:
                    return f"O horário '{valor}' não está disponível para {especialidade.title()} no dia {data}. \n Informe um dos horário disponíveis: {', '.join(horarios_disp)}"
            else:
                return "Você deve escolher a especialidade e a data antes do horário."

        if campo == "confirmar" and valor.lower() not in ['sim', 'não', 'nao']:
            return "Responda 'sim' para confirmar ou 'não' para cancelar."

        if campo == "telefone" and not re.fullmatch(r'\d{8,15}', valor):
            return "Telefone inválido. Informe apenas números, entre 8 e 15 dígitos."

        if campo == "email" and not re.match(r"[^@]+@[^@]+\.[^@]+", valor):
            return "E-mail inválido. Informe no formato exemplo@dominio.com."

        if campo == "nome" and len(valor.strip()) < 3:
            return "Nome muito curto. Informe seu nome completo."

        return None

@agendamento_bp.route('/agendar', methods=['POST'])
def agendar():
    session.setdefault('step_agendamento', 0)
    session.setdefault('dados', {})

    step = session['step_agendamento']
    dados = session['dados']
    user_message = request.json['message'].strip()

    perguntas = [
        "Digite seu nome: (Digite \"sair\" para sair do agendamento 😊)",
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

    if step < len(campos) - 1:
        campo_atual = campos[step]
        erro = validar_campo(campo_atual, user_message, dados)
        if erro:
            return jsonify({'response': erro})

        # Salva dados já tratado (especialidade e exame com valor do banco)
        if campo_atual == "exame" and user_message.lower() == 'nenhum':
            dados[campo_atual] = None
        elif campo_atual == "especialidade":
            with Session(engine) as db:
                especialidade_obj = db.query(Especialidade).filter(
                    func.lower(Especialidade.nome) == user_message.lower()
                ).first()
                if especialidade_obj:
                    dados[campo_atual] = especialidade_obj.nome
                else:
                    dados[campo_atual] = user_message
        elif campo_atual == "exame":
            with Session(engine) as db:
                exame_obj = db.query(Exame).filter(
                    func.lower(Exame.nome) == user_message.lower()
                ).first()
                if exame_obj:
                    dados[campo_atual] = exame_obj.nome
                else:
                    dados[campo_atual] = user_message
        else:
            dados[campo_atual] = user_message

        session['step_agendamento'] = step + 1
        session['dados'] = dados

        proxima_pergunta = perguntas[step + 1]
        texto_opcoes = obter_opcoes_para(campos[step + 1], dados)

        # Monta lista de opções reais para o front
        options_list = []

        if campos[step + 1] == "especialidade":
            with Session(engine) as db:
                options_list = [item.nome.title() for item in db.query(Especialidade).all()]

        elif campos[step + 1] == "exame":
            with Session(engine) as db:
                options_list = [item.nome.title() for item in db.query(Exame).all()]
            options_list.append("Nenhum")

        elif campos[step + 1] == "data":
            especialidade = dados.get("especialidade")
            if especialidade:
                options_list = datas_disponiveis(especialidade)

        elif campos[step + 1] == "hora":
            especialidade = dados.get("especialidade")
            data = dados.get("data")
            if especialidade and data:
                options_list = horarios_disponiveis(especialidade, data)

        elif campos[step + 1] == "confirmar":
            options_list = ["Sim", "Não"]

        return jsonify({
            'response': f"{proxima_pergunta}{texto_opcoes}",
            'options': options_list
        })

    elif step == len(campos) - 1:
        campo_atual = campos[step]
        erro = validar_campo(campo_atual, user_message, dados)
        if erro:
            return jsonify({'response': erro})

        if user_message.lower() == 'sim':
            resultado = process_agendamento(dados)
            resposta = resultado.get('mensagem', 'Erro ao realizar o agendamento.')
            if 'resumo' in resultado:
                resposta += f"\nResumo do agendamento:\n{resultado['resumo']}"
        else:
            resposta = "Agendamento cancelado."

        session.pop('step_agendamento', None)
        session.pop('dados', None)
        session['step'] = 'menu_principal'  # Volta o fluxo global ao menu

        return jsonify({'response': resposta.title(), 'options': ['Voltar ao Menu Principal']})

    return jsonify({'response': "Ocorreu um erro no fluxo de agendamento. Por favor, reinicie."})
