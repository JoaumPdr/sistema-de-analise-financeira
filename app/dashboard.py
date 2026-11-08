import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH para encontrar o pacote 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.financas.analise.analisador import AnalisadorFinanceiro
from src.financas.categorias.gerenciador import GerenciadorCategorias
from src.financas.importacao.servico import ServicoImportacao

# Configuração da página
st.set_page_config(
    page_title="Análise Financeira Pessoal", page_icon="💰", layout="wide"
)

from src.financas.banco import SessionLocal


# Gerenciamento de sessão persistente no session_state com auto-recovery
def get_session_resilient():
    if "db_session" not in st.session_state:
        st.session_state.db_session = SessionLocal()
    return st.session_state.db_session

def safe_execute(query, params=None):
    """Executa uma query e faz rollback e reset da sessão em caso de erro."""
    session = get_session_resilient()
    try:
        return session.execute(query, params or {})
    except Exception:
        session.rollback()
        # Reseta a sessão para evitar estados abortados
        st.session_state.db_session = SessionLocal()
        raise

# Inicializa sessão para uso global na dashboard
session = get_session_resilient()

# Menu de Navegação
st.sidebar.title("💰 Finanças Pessoais")
pagina = st.sidebar.radio(
    "Ir para:",
    ["Visão Geral", "Gastos", "Evolução", "Recorrentes", "Importar CSV", "Categorias"],
)

# --- PÁGINA: IMPORTAR CSV ---
if pagina == "Importar CSV":
    st.header("📤 Importar Extrato CSV")
    st.info(
        "Faça upload do seu arquivo CSV. O sistema validará as datas, valores e categorias."
    )

    uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")
    criar_cats = st.checkbox(
        "Criar categorias automaticamente se não existirem", value=True
    )

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
                        st.warning(
                            "Algumas linhas foram rejeitadas. Veja os detalhes abaixo:"
                        )
                        rejeitados = safe_execute(
                            text(
                                "SELECT numero_linha, motivo, conteudo_bruto FROM registros_rejeitados WHERE importacao_id = (SELECT max(id) FROM importacoes)"
                            )
                        ).fetchall()
                        st.table(
                            [
                                {"Linha": r[0], "Motivo": r[1], "Conteúdo": r[2]}
                                for r in rejeitados
                            ]
                        )

                except Exception as e:  # noqa: BLE001
                    st.error(f"Erro na importação: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# --- PÁGINA: CATEGORIAS ---
elif pagina == "Categorias":
    st.header("🗂️ Gestão de Categorias")
    gerenciador = GerenciadorCategorias(session)

    # Formulário de criação
    with st.expander("➕ Adicionar Nova Categoria"), st.form("nova_categoria"):
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

            status = "Ativa" if cat["ativa"] else "Inativa"
            col2.write(status)

            if col3.button("Alternar Status", key=f"btn_status_{cat['id']}"):
                gerenciador.alternar_status(cat["id"], not cat["ativa"])
                st.rerun()

            if col4.button(
                "Excluir",
                key=f"btn_del_{cat['id']}",
                help="Apenas categorias sem registros podem ser excluídas",
            ):
                # Implementação simples: apenas desativa por segurança conforme instrução
                gerenciador.alternar_status(cat["id"], False)
                st.rerun()

# --- PÁGINA: VISÃO GERAL ---
elif pagina == "Visão Geral":
    st.header("📊 Visão Geral")

    # Filtro de Mês de Referência
    meses_disp = safe_execute(
        text(
            "SELECT DISTINCT DATE_TRUNC('month', data)::DATE as mes FROM vw_movimentacoes ORDER BY mes DESC"
        )
    ).fetchall()
    opcoes_meses = [m[0] for m in meses_disp]

    if not opcoes_meses:
        st.info("Nenhum dado importado ainda. Vá em 'Importar CSV' para começar.")
    else:
        mes_selecionado = st.selectbox(
            "Mês de Referência", opcoes_meses, format_func=lambda d: d.strftime("%m/%Y")
        )

        analisador = AnalisadorFinanceiro(session)

        # Dados do mês selecionado
        inicio_mes = mes_selecionado
        fim_mes = (
            pd.Timestamp(mes_selecionado) + pd.DateOffset(months=1)
        ) - pd.Timedelta(days=1)

        # Gastos por categoria (para calcular total despesas)
        gastos_cat = analisador.gastos_por_categoria(str(inicio_mes), str(fim_mes))
        total_despesas = sum(g["total"] for g in gastos_cat)

        # Receitas do mês
        receitas_mes = safe_execute(
            text("""
            SELECT COALESCE(SUM(valor), 0) FROM receitas 
            WHERE data BETWEEN :ini AND :fim
        """),
            {"ini": inicio_mes, "fim": fim_mes},
        ).scalar()

        saldo = receitas_mes - total_despesas

        # Percentual comprometido
        pct_comp = (total_despesas / receitas_mes * 100) if receitas_mes > 0 else 0

        # Cartões (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "💰 Receitas",
            f"R$ {receitas_mes:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )
        col2.metric(
            "💸 Despesas",
            f"R$ {total_despesas:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )
        col3.metric(
            "⚖️ Saldo",
            f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            delta_color="normal" if saldo >= 0 else "inverse",
        )
        col4.metric(
            "📊 % Comprometido",
            f"{pct_comp:.1f}%",
            delta=f"{pct_comp - 30:.1f}% vs ideal 30%"
            if pct_comp > 30
            else "Dentro do ideal",
        )

        # Gráfico rápido de composição das despesas
        if gastos_cat:
            df_gastos = pd.DataFrame(gastos_cat)
            st.subheader("Composição das Despesas")
            st.bar_chart(df_gastos.set_index("nome_categoria")["total"])

# --- PÁGINA: GASTOS ---
elif pagina == "Gastos":
    st.header("📉 Análise de Gastos por Categoria")

    analisador = AnalisadorFinanceiro(session)

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        data_inicio = st.date_input("Data Início", value=None)
    with col_f2:
        data_fim = st.date_input("Data Fim", value=None)

    if data_inicio and data_fim:
        gastos = analisador.gastos_por_categoria(str(data_inicio), str(data_fim))

        if not gastos:
            st.info("Nenhuma despesa no período selecionado.")
        else:
            df = pd.DataFrame(gastos)

            # Filtro de categorias
            cats_disponiveis = df["nome_categoria"].tolist()
            cats_sel = st.multiselect(
                "Filtrar Categorias", cats_disponiveis, default=cats_disponiveis
            )
            df_filtrado = df[df["nome_categoria"].isin(cats_sel)]

            # Tabela Detalhada
            st.subheader("Tabela Detalhada")
            # Formatação para exibição
            df_show = df_filtrado.copy()
            df_show["total"] = df_show["total"].apply(
                lambda x: (
                    f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
            )
            df_show["percentual"] = df_show["percentual"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show.rename(
                    columns={
                        "nome_categoria": "Categoria",
                        "total": "Total",
                        "percentual": "% do Total",
                    }
                ),
                use_container_width=True,
            )

            # Gráfico
            st.subheader("Gráfico de Gastos")
            st.bar_chart(df_filtrado.set_index("nome_categoria")["total"])
    else:
        st.info("Selecione um período para visualizar os gastos.")

# --- PÁGINA: EVOLUÇÃO ---
elif pagina == "Evolução":
    st.header("📈 Evolução Financeira Mensal")

    analisador = AnalisadorFinanceiro(session)
    evolucao = analisador.evolucao_financeira()

    if not evolucao:
        st.info("Nenhum dado para exibir a evolução.")
    else:
        df = pd.DataFrame(evolucao)
        df["mes"] = pd.to_datetime(df["mes"])

        # Gráfico de Linha
        st.subheader("Receitas, Despesas e Saldo Acumulado")
        st.line_chart(df.set_index("mes")[["receitas", "despesas", "saldo_acumulado"]])

        # Tabela
        st.subheader("Dados Mensais")
        df_show = df.copy()
        for col in ["receitas", "despesas", "saldo", "saldo_acumulado"]:
            df_show[col] = df_show[col].apply(
                lambda x: (
                    f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
            )
        df_show["mes"] = df_show["mes"].dt.strftime("%m/%Y")
        st.dataframe(
            df_show.rename(
                columns={
                    "mes": "Mês",
                    "receitas": "Receitas",
                    "despesas": "Despesas",
                    "saldo": "Saldo",
                    "saldo_acumulado": "Saldo Acumulado",
                }
            ),
            use_container_width=True,
        )

        # Comparação entre dois meses
        st.subheader("🔍 Comparação entre Meses")
        meses = df["mes"].dt.strftime("%m/%Y").tolist()
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            mes1 = st.selectbox("Mês Base", meses, index=len(meses) - 1 if meses else 0)
        with col_c2:
            mes2 = st.selectbox(
                "Mês Comparação", meses, index=len(meses) - 2 if len(meses) > 1 else 0
            )

        if st.button("Comparar"):
            # Usa a consulta 03 (precisa da data base do mês 1)
            # Encontrar a data real do mês 1
            dt_mes1 = df[df["mes"].dt.strftime("%m/%Y") == mes1]["mes"].iloc[0]
            comp = analisador.comparacao_meses(str(dt_mes1))

            if comp:
                df_comp = pd.DataFrame(comp)
                st.dataframe(df_comp, use_container_width=True)
            else:
                st.info("Sem dados para comparação.")

# --- PÁGINA: RECORRENTES ---
elif pagina == "Recorrentes":
    st.header("🔄 Despesas Recorrentes")

    analisador = AnalisadorFinanceiro(session)
    recorrentes = analisador.despesas_recorrentes(tolerancia=0.10)

    if not recorrentes:
        st.info("Nenhuma despesa recorrente detectada (mínimo 3 meses distintos).")
    else:
        df = pd.DataFrame(recorrentes)

        st.metric(
            "Total Mensal Estimado (Recorrentes)",
            f"R$ {df['valor_medio'].sum():,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
        )

        df_show = df.copy()
        df_show["valor_medio"] = df_show["valor_medio"].apply(
            lambda x: (
                f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        )
        df_show["total_mensal_comprometido"] = df_show[
            "total_mensal_comprometido"
        ].apply(
            lambda x: (
                f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        )

        st.dataframe(
            df_show.rename(
                columns={
                    "descricao": "Descrição",
                    "categoria": "Categoria",
                    "valor_medio": "Valor Médio",
                    "meses_distintos": "Meses Distintos",
                    "total_mensal_comprometido": "Comprometimento Mensal",
                }
            ),
            use_container_width=True,
        )
