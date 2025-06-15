from models.db import Paciente, Agendamento, engine
from sqlalchemy.orm import Session

def process_agendamento(dados):
    try:
        with Session(engine) as db:
            # 1. Buscar paciente por e-mail
            paciente = db.query(Paciente).filter_by(email=dados['email']).first()

            # 2. Se não existir, cria
            if not paciente:
                paciente = Paciente(
                    nome=dados['nome'],
                    telefone=dados['telefone'],
                    email=dados['email']
                )
                db.add(paciente)
                db.commit()
                db.refresh(paciente)

            # 3. Criar agendamento
            novo_agendamento = Agendamento(
                paciente_id=paciente.id,
                especialidade=dados['especialidade'],
                data=dados['data'],
                hora=dados['hora'],
                exame=dados.get('exame') or ''
            )
            db.add(novo_agendamento)
            db.commit()

            # 4. Retorno
            resumo = (
                f"Paciente: {paciente.nome}\n"
                f"Telefone: {paciente.telefone}\n"
                f"E-mail: {paciente.email}\n"
                f"Especialidade: {novo_agendamento.especialidade}\n"
                f"Exame: {novo_agendamento.exame or 'Nenhum'}\n"
                f"Data: {novo_agendamento.data}\n"
                f"Hora: {novo_agendamento.hora}"
            )

            return {
                'mensagem': "✅ Agendamento realizado com sucesso!",
                'resumo': resumo
            }

    except Exception as e:
        return {'erro': f"Erro ao agendar: {str(e)}"}
