
import pytest

from src.financas.banco import get_session
from src.financas.importacao.servico import ServicoImportacao
from src.financas.modelos import (
    Categoria,
    Despesa,
    Importacao,
    Receita,
    RegistroRejeitado,
)


@pytest.fixture
def db_session():
    # Obtém a sessão do generator
    session = next(get_session())
    yield session
    # Limpa as tabelas na ordem correta para evitar violação de chave estrangeira
    session.query(Receita).delete()
    session.query(Despesa).delete()
    session.query(RegistroRejeitado).delete()
    session.query(Importacao).delete()
    session.query(Categoria).delete()
    session.commit()

def test_importacao_csv_exemplo(db_session):
    caminho_csv = "data/exemplo/extrato_teste.csv"
    
    # Instancia o serviço com a sessão do banco
    servico = ServicoImportacao(db_session)
    
    # Executa a importação (habilitando criação de categorias para o teste)
    resultado = servico.importar_csv(caminho_csv, criar_categorias=True)
    
    # Verifica o resumo (baseado no extrato_teste.csv)
    assert resultado["lidas"] > 0
    assert resultado["aceitas"] > 0
    assert resultado["rejeitadas"] > 0
    
    # Verifica se os registros foram inseridos no banco
    total_receitas = db_session.query(Receita).count()
    total_despesas = db_session.query(Despesa).count()
    assert (total_receitas + total_despesas) == resultado["aceitas"]

def test_idempotencia_importacao(db_session):
    caminho_csv = "data/exemplo/extrato_teste.csv"
    servico = ServicoImportacao(db_session)
    
    # Primeira importação
    res1 = servico.importar_csv(caminho_csv, criar_categorias=True)
    
    # Segunda importação (mesmo arquivo)
    res2 = servico.importar_csv(caminho_csv, criar_categorias=True)
    
    # Verifica se a segunda importação não adicionou registros (aceitas deve ser 0)
    assert res2["aceitas"] == 0
    # O número de duplicatas deve ser igual ao número de aceitos da primeira vez
    assert res2["duplicadas"] == res1["aceitas"]
