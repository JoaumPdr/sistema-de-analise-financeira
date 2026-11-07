# RELATÓRIO DE DESENVOLVIMENTO - Sistema de Análise Financeira Pessoal

## Quadro de Status
- F0: Estrutura inicial [concluída]
- F1: Modelo de dados [concluída]
- F2: Importação e validação [concluída]
- F3: Consultas SQL de análise [concluída]
- F4: Categorias [concluída]
- F5: Dashboard [concluída]
- F6: Documentação e fechamento [concluída]

---

### F0 — Estrutura Inicial (06/11/2026)
**Objetivo:** Criar repositório, pastas, configs base e docs iniciais.
**Playbook:** `direct`.
**Feito:** Git init, `docker-compose.yml` (Postgres), `pyproject.toml`, `.env.example`, `.gitignore`, estrutura de pastas `src/`, `sql/`, `tests/`, `data/`. Docs base (`README`, `design`, `RELATORIO`).
**Decisões:** Stack definida (Python, Pandas, Postgres, SQLAlchemy, Streamlit, Alembic). Convenções de commit/branch PT-BR.
**Testes:** `pytest` e `ruff` configurados (passam vazios).
**Próximos:** Modelo de dados.

### F1 — Modelo de Dados (06/11/2026)
**Objetivo:** Definir schema, ORM e migração inicial.
**Playbook:** `plan-execute` (camada `strong` para decisões de schema).
**Feito:** `modelos.py` com 5 tabelas + view. `NUMERIC(12,2)` para dinheiro. Alembic configurado e migração `615a9cda8c5b` gerada/aplicada. View `vw_movimentacoes` criada via SQL.
**Decisões:** Tabelas separadas Receitas/Despesas. Hash SHA-256 para idempotência. Índice único categoria por tipo.
**Testes:** Migração sobe/desce sem erro. Constraints validadas via inspeção.
**Problemas:** Docker não rodava inicialmente; resolvido iniciando Docker Desktop.
**Próximos:** Importação CSV.

### F2 — Importação e Validação (06/11/2026)
**Objetivo:** Pipeline robusto de leitura CSV → Validação → Banco.
**Playbook:** `plan-execute` + `cascade` nos validadores (camada `strong` para regras de dinheiro/validação).
**Feito:** 
- `normalizadores.py`: Detecção encoding/separador, parsing Decimal/Datas BR.
- `validador.py`: 7 regras implementadas (colunas, datas, valores>0, tipo, descrição, categoria, hash duplicata).
- `servico.py`: Orquestração transacional, hash arquivo/registro, resumo lidas/aceitas/rejeitadas/duplicadas.
- `data/exemplo/extrato_teste.csv`: 35 linhas com casos de borda (inválidos, duplicata, recorrentes, mês sem receita).
- `banco.py`: Gestão de sessão SQLAlchemy scoped.
- Testes `test_importacao.py`: Valida importação, idempotência (reimportar = 0 aceitas, duplicatas = aceitas anterior).
**Decisões:** Valor negativo rejeitado (sinal vem do campo `tipo`). Duplicata checada por hash antes do INSERT. Linhas ruins vão para `registros_rejeitados`.
**Problemas:** CSV inicial tinha aspas quebrando parser Pandas → corrigido aspas nas descrições. Ordem de delete nos testes violava FK → corrigido para deletar filhos antes dos pais.
**Próximos:** Consultas de análise.

### F3 — Consultas SQL de Análise (06/11/2026)
**Objetivo:** 6 consultas analíticas parametrizadas em arquivos `.sql`.
**Playbook:** `plan-execute` (camada `strong` para cálculos financeiros).
**Feito:** 
1. `01_gastos_por_categoria.sql` (Total + %).
2. `02_media_despesas_mensais.sql` (Média últimos N meses).
3. `03_comparacao_entre_meses.sql` (FULL OUTER JOIN, variação % com NULL se mês anterior inexistente).
4. `04_despesas_recorrentes.sql` (Agrupamento descrição+categoria, >=3 meses distintos).
5. `05_percentual_renda_comprometida.sql` (CASE WHEN receitas=0 THEN NULL).
6. `06_evolucao_financeira.sql` (Window Function SUM OVER para saldo acumulado).
- `analisador.py`: Wrapper Python que lê `.sql` e executa via `text()`.
**Decisões:** SQL em arquivos separados (manutenibilidade, revisão). Parâmetros nomeados (`:param`) para segurança. Divisão por zero tratada em todas as queries.
**Próximos:** Gestão de Categorias.

### F4 — Categorias (07/11/2026)
**Objetivo:** CRUD de categorias com soft-delete.
**Playbook:** `direct`.
**Feito:** `gerenciador.py` (listar, criar, editar, alternar status). Validação unicidade nome+tipo. `test_categorias.py` (5 testes: sucesso, duplicata, mesmo nome tipo diferente, toggle status, edição).
**Decisões:** Soft delete (`ativa` boolean) para preservar histórico. Permitir mesmo nome para tipos diferentes (ex: "Salário" receita e "Salário" despesa - embora improvável).
**Próximos:** Dashboard.

### F5 — Dashboard (07/11/2026)
**Objetivo:** Interface Web Streamlit consumindo apenas F3/F4.
**Playbook:** `plan-execute`.
**Feito:** `app/dashboard.py` com 6 páginas:
1. **Importar CSV**: Upload, métricas, tabela erros.
2. **Categorias**: Formulário + lista com botões ativar/desativar.
3. **Visão Geral**: 4 KPIs (Receitas, Despesas, Saldo, % Comprometido) + gráfico barras.
4. **Gastos**: Filtros data + multiselect categorias, tabela + gráfico.
5. **Evolução**: Line chart (Receitas, Despesas, Saldo Acumulado), tabela, comparador 2 meses (usa Consulta 3).
6. **Recorrentes**: Tabela detecção automática + total mensal estimado.
- Formatação PT-BR (R$ 1.234,56, DD/MM/AAAA). Estados vazios amigáveis. Layout wide responsivo.
**Decisões:** Sessão DB em `st.session_state`. Sem cache de dados (volume baixo), recalcula a cada interação.
**Próximos:** Documentação final.

### F6 — Documentação e Fechamento (07/11/2026)
**Objetivo:** Entregar documentação completa e validar projeto.
**Playbook:** `direct` + `review-gate` final.
**Feito:**
- **README.md**: Reescrito com passos testáveis (Docker, Venv, Alembic, Streamlit, Importação exemplo).
- **design.md**: Registradas todas as decisões (arquitetura, modelo, dinheiro, validação, queries, dashboard, qualidade).
- **RELATORIO.md**: Esta entrada cumulativa finalizando o quadro de status.
- **Validação Final**: `pytest` (suíte completa passa), `ruff check .` (sem erros).
**Critério de Aceite Final:** Um desenvolvedor iniciante consegue seguir o README do zero e ver o dashboard funcionando com o CSV de exemplo.
