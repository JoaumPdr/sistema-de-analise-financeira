import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()


# Cache para o engine de teste (singleton) - necessário para SQLite in-memory
# que cria um novo DB a cada engine se não for compartilhado
_test_engine = None


def get_database_url(test: bool = False) -> str:
    """
    Retorna a URL do banco de dados.
    Se test=True, usa DATABASE_TEST_URL ou SQLite in-memory como fallback.
    """
    if test:
        return os.getenv("DATABASE_TEST_URL", "sqlite:///:memory:")
    return os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://usuario:senha@localhost:5432/financas_db"
    )


def get_engine(test: bool = False):
    """Cria engine SQLAlchemy. Para test=True, reutiliza o engine cached (singleton)."""
    global _test_engine

    if test:
        if _test_engine is None:
            url = get_database_url(test=True)
            connect_args = (
                {"check_same_thread": False} if url.startswith("sqlite") else {}
            )
            _test_engine = create_engine(
                url, pool_pre_ping=True, connect_args=connect_args, echo=False
            )
        return _test_engine

    url = get_database_url(test=False)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args, echo=False)


# Engine padrão (produção/desenvolvimento)
engine = get_engine(test=False)
SessionLocal = sessionmaker(bind=engine)
Session = scoped_session(SessionLocal)


# Session factory para testes (usa o engine cached)
_test_session_factory = None


def _get_test_session_factory():
    """Retorna session factory para testes, criando se necessário."""
    global _test_session_factory
    if _test_session_factory is None:
        _test_session_factory = sessionmaker(bind=get_engine(test=True))
    return _test_session_factory


def get_session(test: bool = False):
    """
    Generator que fornece uma sessão do banco de dados.
    Uso: with next(get_session()) as session: ...
    """
    if test:
        TestSession = scoped_session(_get_test_session_factory())
        session = TestSession()
        try:
            yield session
        finally:
            TestSession.remove()
    else:
        session = Session()
        try:
            yield session
        finally:
            Session.remove()


def create_tables(test: bool = False):
    """Cria todas as tabelas (útil para testes com SQLite)."""
    from src.financas.modelos import Base

    eng = get_engine(test)
    Base.metadata.create_all(eng)


def reset_test_database():
    """Reseta o banco de teste (drop + create). Útil para limpeza entre suítes."""
    # ruff: noqa: PLW0602  # False positive: _test_engine is assigned in conditional block
    global _test_engine, _test_session_factory
    from src.financas.modelos import Base

    if _test_engine is not None:
        Base.metadata.drop_all(_test_engine)
        Base.metadata.create_all(_test_engine)
    _test_session_factory = None  # Força recriação
