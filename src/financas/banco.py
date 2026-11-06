import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

load_dotenv()

# Pega a URL do banco de dados do arquivo .env ou usa o padrão do exemplo
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://usuario:senha@localhost:5432/financas_db")

# Criação do engine SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, # Verifica se a conexão ainda está ativa
    echo=False          # Mude para True se quiser ver os SQLs no console
)

# Configuração da sessão
# scoped_session garante que a mesma sessão seja usada dentro de um mesmo contexto (ex: request)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_session():
    """
    Generator que fornece uma sessão do banco de dados.
    Uso: with next(get_session()) as session: ...
    """
    session = Session()
    try:
        yield session
    finally:
        Session.remove()
