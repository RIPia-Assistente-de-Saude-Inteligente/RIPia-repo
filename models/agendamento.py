from .db import horarios, agendamentos

def process_agendamento(dados):
    disponivel = horarios.find_one({
        "especialidade": dados["especialidade"],
        "data": dados["data"],
        "hora": dados["hora"],
        "disponivel": True
    })
    if not disponivel:
        return {"erro": "Horário indisponível"}
    agendamentos.insert_one({**dados, "status": "Confirmado"})
    horarios.update_one({"_id": disponivel["_id"]}, {"$set": {"disponivel": False}})
    resumo = (
        f"Nome: {dados['nome']}\n"
        f"Telefone: {dados['telefone']}\n"
        f"E-mail: {dados['email']}\n"
        f"Especialidade: {dados['especialidade']}\n"
        f"Exame: {dados['exame'] if dados['exame'] else 'Nenhum'}\n"
        f"Data: {dados['data']}\n"
        f"Hora: {dados['hora']}"
    )
    return {"mensagem": "✅ Agendamento confirmado com sucesso!", "resumo": resumo}