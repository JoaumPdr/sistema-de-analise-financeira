from src.financas.importacao.servico import ServicoImportacao
from src.financas.modelos import Despesa, Receita


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
    servico.importar_csv(caminho_csv, criar_categorias=True)

    # Segunda importação (mesmo arquivo)
    res2 = servico.importar_csv(caminho_csv, criar_categorias=True)

    # Verifica se a segunda importação não adicionou registros (aceitas deve ser 0)
    assert res2["aceitas"] == 0
    # O número de duplicatas deve ser igual ao número de registros válidos no arquivo
    # No extrato_teste.csv, temos 35 linhas, 2 são inválidas (Valor negativo e Descrição Vazia),
    # sobrando 33 linhas que geram hash de duplicata.
    assert res2["duplicadas"] == 33
