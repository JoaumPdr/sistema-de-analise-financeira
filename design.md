# Design do Sistema - Análise Financeira Pessoal

## 1. Arquitetura Geral

O sistema segue uma arquitetura em camadas desacoplada:

```
[Interface: Streamlit] 
      ↓
[Camada de Análise: src/financas/analise] ← Executa SQLs parametrizados
      ↓
[Camada de Domínio: src/financas/importacao, categorias] ← Regras de negócio
      ↓
[Camada de Dados: src/financas/modelos, banco] ← SQLAlchemy + PostgreSQL
```

**Princípios:**
- **Separação de Responsabilidades**: SQL fica em arquivos `.sql` (pasta `sql/analise`), não no código Python.
- **Injeção de Dependência**: Sessão do banco passada explicitamente para os serviços.
- **Imutabilidade de Dados Brutos**: CSVs importados geram registros em `importacoes` e `registros_rejeitados`; nada é perdido.

---

## 2. Modelo de Dados

### Tabelas Principais

| Tabela | Finalidade | Decisões Chave |
|--------|------------|----------------|
| `categorias` | Classificação de receitas/despesas | Nome único por tipo (`receita`/`despesa`). Campo `ativa` para soft-delete. |
| `receitas` | Entradas financeiras | `valor NUMERIC(12,2) > 0`. `hash_registro` único (SHA-256 de data+desc+valor+tipo). |
| `despesas` | Saídas financeiras | Mesma estrutura de `receitas`. Separação facilita validações e queries. |
| `importacoes` | Auditoria de arquivos processados | `hash_arquivo` (SHA-256) para detectar reimportação do mesmo arquivo. Contadores de lidas/aceitas/rejeitadas. |
| `registros_rejeitados` | Rastreabilidade de erros | Guarda linha, motivo e conteúdo bruto. FK para `importacoes`. |
| `vw_movimentacoes` | View unificada | `UNION ALL` de receitas e despesas com coluna `tipo`. Base para análises temporais. |

### Justificativas de Modelagem

1.  **Tabelas Separadas (Receitas/Despesas) vs Tabela Única**
    *   *Decisão*: Tabelas separadas.
    *   *Contexto*: Regras de validação e categorias são distintas por tipo.
    *   *Alternativa*: Tabela `movimentacoes` com coluna `tipo`.
    *   *Consequência*: Schema mais verboso, mas integridade referencial mais forte (FK para categorias do tipo correto). View `vw_movimentacoes` resolve a necessidade de consultas unificadas.

2.  **Dinheiro: `NUMERIC(12,2)` / `Decimal`**
    *   *Decisão*: Proibido `float`/`real`.
    *   *Justificativa*: Precisão exata em somas, médias e percentuais. Evita erros de ponto flutuante (ex: `0.1 + 0.2 != 0.3`).

3.  **Chave de Idempotência: `hash_registro`**
    *   *Decisão*: SHA-256 de `(data, descricao_normalizada, valor, tipo)`.
    *   *Justificativa*: Garante que a mesma linha lógica nunca seja inserida duas vezes, mesmo se o CSV for reimportado ou editado externamente mantendo o conteúdo semântico.

4.  **Soft Delete em Categorias (`ativa` boolean)**
    *   *Decisão*: Não excluir, apenas desativar.
    *   *Justificativa*: Preserva integridade histórica. Relatórios passados mantêm o nome da categoria original.

---

## 3. Importação e Validação (F2)

### Pipeline de Processamento
1.  **Detecção**: Encoding (UTF-8 → Latin-1 fallback) e Separador (`,` ou `;`).
2.  **Normalização**: 
    *   Datas: `DD/MM/AAAA` ou `AAAA-MM-DD` → `date`.
    *   Valores: `1.234,56` ou `1234.56` → `Decimal`.
3.  **Validação (7 Regras)**:
    1.  Colunas obrigatórias presentes.
    2.  Data válida e não futura (> 2 anos).
    3.  Valor `Decimal > 0`.
    4.  Tipo ∈ `{receita, despesa}`.
    5.  Descrição não vazia (trim).
    6.  Categoria existe (ou cria se flag ligada).
    7.  `hash_registro` não existe no banco.
4.  **Persistência Transacional**: Tudo ou nada. `registros_rejeitados` populado para linhas inválidas.

### CSV de Exemplo (`data/exemplo/extrato_teste.csv`)
Contém intencionalmente:
- 6 meses de dados (Jan-Jun).
- Linhas inválidas: descrição vazia, valor negativo, data futura (2099).
- Duplicata exata (Salário Jan).
- Categoria inexistente.
- Recorrências: Aluguel, Internet, Netflix, Energia.
- Mês sem receita (Junho).

---

## 4. Consultas de Análise (F3)

Arquivos em `sql/analise/`, executados via `AnalisadorFinanceiro`.

| # | Arquivo | Função | Tratamento de Borda |
|---|---------|--------|---------------------|
| 1 | `01_gastos_por_categoria.sql` | Total + % por cat. | `NULLIF(total_geral, 0)` evita div/0. |
| 2 | `02_media_despesas_mensais.sql` | Média últimos N meses | Agrupa por `DATE_TRUNC('month', data)`. |
| 3 | `03_comparacao_entre_meses.sql` | Mês Atual vs Anterior | `FULL OUTER JOIN`. `NULL` se mês anterior inexistente. |
| 4 | `04_despesas_recorrentes.sql` | Detecção recorrência | `COUNT(DISTINCT mes) >= 3`. Agrupa por descrição exata + categoria. |
| 5 | `05_percentual_renda_comprometida.sql` | % Despesas/Receitas | `CASE WHEN receitas=0 THEN NULL`. |
| 6 | `06_evolucao_financeira.sql` | Série temporal + saldo acumulado | Window Function `SUM(saldo) OVER (ORDER BY mes)`. |

**Parametrização**: Todas usam `:parametros` (SQLAlchemy `text()`), nunca concatenação de strings.

---

## 5. Dashboard (F5 - Streamlit)

### Páginas e Fontes de Dados
| Página | Fonte Principal | Recursos UI |
|--------|-----------------|-------------|
| Importar CSV | `ServicoImportacao` | `st.file_uploader`, métricas, tabela de erros. |
| Categorias | `GerenciadorCategorias` | Formulário, lista com botões de ação (ativar/desativar). |
| Visão Geral | Consulta 1 + Query Receitas | 4 KPIs (`st.metric`), gráfico de barras composição. |
| Gastos | Consulta 1 | Filtros data + multiselect categorias, tabela + gráfico. |
| Evolução | Consulta 6 + Consulta 3 | `st.line_chart` (3 séries), tabela formatada, comparador 2 meses. |
| Recorrentes | Consulta 4 | Métrica total, tabela formatada. |

### Formatação e UX
- **Moeda**: `R$ 1.234,56` (replace hack Python para locale pt-BR).
- **Datas**: `DD/MM/AAAA` (`strftime`).
- **Estados Vazios**: `st.info` com instruções contextuais.
- **Layout**: `layout="wide"`, `st.columns` para responsividade.
- **Cache**: Sessão DB em `st.session_state` (evita reconexão). Dados recalculados a cada interação (dado volume esperado baixo).

---

## 6. Qualidade e Processo (Seção 0)

### Branches e Commits
- **Main**: Sempre estável. Merge `--no-ff` preserva histórico da feature branch.
- **Branches**: `tipo/descricao` (ex: `feat/importacao-csv`, `fix/validacao-data`).
- **Commits**: Conventional Commits PT-BR (`feat(banco): adiciona indice...`).
- **Tags**: `fase-F0` a `fase-F5` marcam conclusão de cada fase.

### Documentação Viva
- `README.md`: Testado seguindo os próprios passos.
- `design.md`: Atualizado a cada decisão arquitetural (este arquivo).
- `RELATORIO.md`: Entrada por fase com decisões, problemas e testes.

### Testes e Lint
- **Pytest**: Isolamento via fixture `db_session` (rollback/limpeza por teste).
- **Ruff**: Linha 88, regras padrão.
- **Cobertura**: F2 (validações, idempotência), F4 (CRUD categorias).

---

## 7. Decisões Técnicas Adicionais

1.  **Alembic para Migrações**: Obrigatório. Nada de `CREATE TABLE` manual. Versionamento garante reprodutibilidade.
2.  **Docker Compose Apenas para DB**: Aplicação roda nativamente no host (venv). Simplifica debug e hot-reload do Streamlit.
3.  **`python-dotenv`**: Carrega `.env` automaticamente no `banco.py`. Facilita troca de ambiente (dev/prod).
4.  **Hash de Arquivo (`importacoes.hash_arquivo`)**: Permite detectar se o *mesmo arquivo físico* já foi processado, otimizando importações grandes.
5.  **Tolerância Recorrência (F3 Consulta 4)**: Implementada como agrupamento por descrição exata. Melhoria futura: fuzzy matching (Levenshtein) para "Netflix" vs "Netflix.com".

---

## 8. Próximos Passos / Melhorias Futuras (Backlog)

- [ ] Autenticação multiusuário (atual: uso individual).
- [ ] Importação OFX/QIF além de CSV.
- [ ] Fuzzy matching para detecção de recorrência (ex: "Uber *123" vs "Uber *456").
- [ ] Gráficos Plotly interativos (zoom, tooltip) no lugar dos nativos do Streamlit.
- [ ] Exportação de relatórios para PDF/Excel.
- [ ] Testes de integração end-to-end (Playwright/Cypress para UI).