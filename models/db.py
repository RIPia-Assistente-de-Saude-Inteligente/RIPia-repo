import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["clinica"]
especialidades = db["especialidades"]
exames = db["exames"]
horarios = db["horarios"]
agendamentos = db["agendamentos"]

# Dados iniciais
if especialidades.count_documents({}) == 0:
    especialidades.insert_many([
        {"nome": "Clínico Geral"},
        {"nome": "Cardiologia"},
        {"nome": "Dermatologia"}
    ])

if exames.count_documents({}) == 0:
    exames.insert_many([
        {"nome": "Hemograma"},
        {"nome": "Raio-X"},
        {"nome": "Eletrocardiograma"}
    ])

if horarios.count_documents({}) == 0:
    horarios.insert_many([
        {"especialidade": "Clínico Geral", "data": "12/06/2025", "hora": "09:00", "disponivel": True},
        {"especialidade": "Clínico Geral", "data": "12/06/2025", "hora": "10:00", "disponivel": True},
        {"especialidade": "Cardiologia", "data": "13/06/2025", "hora": "14:00", "disponivel": True},
        {"especialidade": "Dermatologia", "data": "14/06/2025", "hora": "16:00", "disponivel": True}
    ])