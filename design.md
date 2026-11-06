# Design do Sistema - Análise Financeira Pessoal

## Arquitetura
O sistema é composto por:
- Banco de Dados: PostgreSQL (via Docker)
- ORM: SQLAlchemy
- Migrações: Alembic
- Processamento: Pandas
- Interface: Streamlit

## Decisões Técnicas
- **Tipos de Dados para Dinheiro:** Decidido utilizar `NUMERIC(12,2)` no PostgreSQL e `Decimal` no Python.
  - **Contexto:** O uso de `float` ou `real` causa erros de arredondamento em cálculos financeiros.
  - **Alternativas:** `Integer` (armazenando centavos), mas `NUMERIC` é o padrão SQL para precisão decimal fixa.
  - **Consequência:** Precisão absoluta em somas e médias, essencial para relatórios financeiros.

- **Modelo de Dados:** Tabelas separadas para `receitas` e `despesas`.
  - **Contexto:** Facilita a aplicação de regras de validação distintas e a gestão de categorias específicas por tipo.
  - **Alternativa:** Tabela única `movimentacoes` com coluna `tipo`.
  - **Consequência:** Maior clareza no schema, embora exija a `vw_movimentacoes` para visões consolidadas.

