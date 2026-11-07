import streamlit as st
from src.financas.banco import get_session
from src.financas.importacao.servico import ServicoImportacao
from src.financas.categorias.gerenciador import GerenciadorCategorias
from src.financas.analise.analisador import AnalisadorFinanceiro

# Configuração da página
st.set_page_config(
    page_title="Análise Financeira Pessoal",
    page_icon="💰",
    layout="wide"
)

# Inicialização da sessão do banco de dados no session_state
if 'db_session' not in st.session_state:
    st.session_state.db_session = next(get_session())

session = st.session_state.db_session

# Menu de Navegação
st.sidebar.title("💰 Finanças Pessoais")
pagina = st.sidebar.radio(
    "Ir para:",
    ["Visão Geral", "Gastos", "Evolução", "Recorrentes", "Importar CSV", "Categorias"]
)

# --- PÁGINA: IMPORTAR CSV ---
if pagina == "Importar CSV":
    st.header("📤 Importar Extrato CSV")
    st.info("Faça upload do seu arquivo CSV. O sistema validará as datas, valores e categorias.")
    
    uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")
    criar_cats = st.checkbox("Criar categorias automaticamente se não existirem", value=True)
    
    if uploaded_file is not None:
        # Salva temporariamente para o serviço de importação ler o caminho
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Iniciar Importação"):
            with st.spinner("Processando arquivo..."):
                try:
                    servico = ServicoImportacao(session)
                    res = servico.importar_csv(temp_path, criar_categorias=criar_cats)
                    
                    st.success("Importação concluída!")
                    
                    # Exibição do resumo em colunas
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Lidas", res["lidas"])
                    col2.metric("Aceitas", res["aceitas"])
                    col3.metric("Rejeitadas", res["rejeitadas"])
                    col4.metric("Duplicadas", res["duplicadas"])
                    
                    if res["rejeitadas"] > 0:
                        st.warning("Algumas linhas foram rejeitadas. Veja os detalhes abaixo:")
                        rejeitados = session.execute(
                            text("SELECT numero_linha, motivo, conteudo_bruto FROM registros_rejeitados WHERE importacao_id = (SELECT max(id) FROM importacoes)")
                        ).fetchall()
                        st.table([{"Linha": r[0], "Motivo": r[1], "Conteúdo": r[2]} for r in rejeitados])
                        
                except Exception as e:
                    st.error(f"Erro na importação: {e}")
                finally:
                    import os
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# --- PÁGINA: CATEGORIAS ---
elif pagina == "Categorias":
    st.header("🗂️ Gestão de Categorias")
    gerenciador = GerenciadorCategorias(session)
    
    # Formulário de criação
    with st.expander("➕ Adicionar Nova Categoria"):
        with st.form("nova_categoria"):
            nome = st.text_input("Nome da Categoria")
            tipo = st.selectbox("Tipo", ["despesa", "receita"])
            submit = st.form_submit_button("Criar")
            
            if submit:
                if nome:
                    nova = gerenciador.criar_categoria(nome, tipo)
                    if nova:
                        st.success(f"Categoria '{nome}' criada!")
                        st.rerun()
                    else:
                        st.error("Esta categoria já existe para o tipo selecionado.")
                else:
                    st.error("Por favor, insira um nome.")

    # Listagem e Gestão
    st.subheader("Categorias Cadastradas")
    categorias = gerenciador.listar_categorias(apenas_ativas=False)
    
    if not categorias:
        st.info("Nenhuma categoria cadastrada.")
    else:
        for cat in categorias:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(f"**{cat['nome']}** ({cat['tipo']})")
            
            status = "Ativa" if cat['ativa'] else "Inativa"
            col2.write(status)
            
            if col3.button(f"Alternar Status", key=f"btn_status_{cat['id']}"):
                gerenciador.alternar_status(cat['id'], not cat['ativa'])
                st.rerun()
            
            if col4.button(f"Excluir", key=f"btn_del_{cat['id']}", help="Apenas categorias sem registros podem ser excluídas"):
                # Implementação simples: apenas desativa por segurança conforme instrução
                gerenciador.alternar_status(cat['id'], False)
                st.rerun()

# --- PÁGINAS DE ANÁLISE (A serem implementadas na próxima unidade) ---
elif pagina == "Visão Geral":
    st.header("📊 Visão Geral")
    st.info("Implementando cartões de resumo... (Aguardando Unidade 3)")

elif pagina == "Gastos":
    st.header("📉 Análise de Gastos")
    st.info("Implementando gráficos de categoria... (Aguardando Unidade 3)")

elif pagina == "Evolução":
    st.header("📈 Evolução Financeira")
    st.info("Implementando série temporal... (Aguardando Unidade 4)")

elif pagina == "Recorrentes":
    st.header("🔄 Despesas Recorrentes")
    st.info("Implementando detecção de recorrências... (Aguardando Unidade 4)")

# Importações necessárias para o código acima
from sqlalchemy import text
