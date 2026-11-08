import pytest

from src.financas.banco import get_engine
from src.financas.modelos import Base

# Engine persistente para o banco SQLite em memória durante a sessão
_test_engine = None


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Cria as tabelas no banco de testes (SQLite in-memory) uma única vez por sessão."""
    global _test_engine
    _test_engine = get_engine(test=True)
    Base.metadata.create_all(_test_engine)
    yield
    _test_engine.dispose()


@pytest.fixture
def db_session():
    """Fornece uma sessão isolada para cada teste, limpando os dados após o uso."""
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=_test_engine)
    session = Session()

    yield session

    # Limpa todas as tabelas após cada teste para garantir isolamento
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
