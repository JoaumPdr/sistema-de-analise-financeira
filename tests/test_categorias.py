from src.financas.categorias.gerenciador import GerenciadorCategorias


def test_criar_categoria_sucesso(db_session):
    gerenciador = GerenciadorCategorias(db_session)
    cat = gerenciador.criar_categoria("Alimentação", "despesa")
    assert cat is not None
    assert cat.nome == "Alimentação"


def test_criar_categoria_duplicada(db_session):
    gerenciador = GerenciadorCategorias(db_session)
    gerenciador.criar_categoria("Lazer", "despesa")
    # Tentando criar a mesma categoria para o mesmo tipo
    cat_dup = gerenciador.criar_categoria("Lazer", "despesa")
    assert cat_dup is None


def test_criar_categoria_mesmo_nome_tipo_diferente(db_session):
    gerenciador = GerenciadorCategorias(db_session)
    gerenciador.criar_categoria("Extra", "receita")
    # Mesmo nome, mas tipo diferente deve ser permitido
    cat_extra = gerenciador.criar_categoria("Extra", "despesa")
    assert cat_extra is not None


def test_alternar_status_categoria(db_session):
    gerenciador = GerenciadorCategorias(db_session)
    cat = gerenciador.criar_categoria("Saúde", "despesa")

    # Desativar
    gerenciador.alternar_status(cat.id, False)
    assert gerenciador.listar_categorias(apenas_ativas=True) == []
    assert len(gerenciador.listar_categorias(apenas_ativas=False)) == 1


def test_editar_categoria(db_session):
    gerenciador = GerenciadorCategorias(db_session)
    cat = gerenciador.criar_categoria("Educação", "despesa")

    sucesso = gerenciador.editar_categoria(cat.id, "Cursos")
    assert sucesso is True
    assert cat.nome == "Cursos"
