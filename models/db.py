from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Conexão com SQLite
engine = create_engine("sqlite:///clinica.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# === Modelos ===
class Especialidade(Base):
    __tablename__ = 'especialidades'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)

class Exame(Base):
    __tablename__ = 'exames'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)

class Horario(Base):
    __tablename__ = 'horarios'
    id = Column(Integer, primary_key=True)
    especialidade = Column(String, nullable=False)
    data = Column(String, nullable=False)   # formato: "12/06/2025"
    hora = Column(String, nullable=False)   # formato: "09:00"
    disponivel = Column(Boolean, default=True)

class Paciente(Base):
    __tablename__ = 'pacientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Agendamento(Base):
    __tablename__ = 'agendamentos'
    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey('pacientes.id'))
    paciente = relationship("Paciente", backref="agendamentos")
    especialidade = Column(String, nullable=False)
    data = Column(String, nullable=False)
    hora = Column(String, nullable=False)
    exame = Column(String)

# Cria as tabelas
Base.metadata.create_all(engine)

# === Inserção de dados iniciais ===

# Especialidades
if session.query(Especialidade).count() == 0:
    session.add_all([
        Especialidade(nome="clínico geral"),
        Especialidade(nome="cardiologia"),
        Especialidade(nome="dermatologia")
    ])

# Exames
if session.query(Exame).count() == 0:
    session.add_all([
        Exame(nome="hemograma"),
        Exame(nome="raio-x"),
        Exame(nome="eletrocardiograma")
    ])

# Horários
if session.query(Horario).count() == 0:
    session.add_all([
        Horario(especialidade="clínico geral", data="12/06/2025", hora="09:00", disponivel=True),
        Horario(especialidade="clínico geral", data="12/06/2025", hora="10:00", disponivel=True),
        Horario(especialidade="cardiologia", data="13/06/2025", hora="14:00", disponivel=True),
        Horario(especialidade="dermatologia", data="14/06/2025", hora="16:00", disponivel=True),
    ])

# Commit e fechamento
session.commit()
session.close()
