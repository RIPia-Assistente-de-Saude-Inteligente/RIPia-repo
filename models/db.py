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
        {"nome": "clínico geral"},
        {"nome": "cardiologia"},
        {"nome": "dermatologia"}
    ])

if exames.count_documents({}) == 0:
    exames.insert_many([
        {"nome": "hemograma"},
        {"nome": "raio-x"},
        {"nome": "eletrocardiograma"}
    ])

if horarios.count_documents({}) == 0:
    horarios.insert_many([
        {"especialidade": "clínico geral", "data": "12/06/2025", "hora": "09:00", "disponivel": True},
        {"especialidade": "clínico geral", "data": "12/06/2025", "hora": "10:00", "disponivel": True},
        {"especialidade": "cardiologia", "data": "13/06/2025", "hora": "14:00", "disponivel": True},
        {"especialidade": "dermatologia", "data": "14/06/2025", "hora": "16:00", "disponivel": True}
    ])