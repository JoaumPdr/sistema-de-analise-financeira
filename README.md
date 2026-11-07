# Sistema de Análise Financeira Pessoal

Sistema para importação de extratos bancários via CSV e análise de finanças pessoais com dashboard interativo.

## 🚀 Stack Tecnológica
- **Python 3.10+**
- **PostgreSQL 15** (via Docker)
- **SQLAlchemy 2.0** + **Alembic** (ORM e Migrações)
- **Pandas** (Processamento de CSV)
- **Streamlit** (Dashboard Web)
- **Pytest** + **Ruff** (Testes e Linting)

---

## 📋 Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Compose instalados
- [Python 3.10+](https://www.python.org/downloads/)
- Git (opcional, para clonar)

---

## ⚙️ Instalação e Configuração

### 1. Clone o repositório (ou baixe os arquivos)
```bash
git clone <url-do-repositorio>
cd financas-pessoais
```

### 2. Suba o Banco de Dados (PostgreSQL)
```bash
docker-compose up -d
```
> Aguarde alguns segundos para o banco inicializar completamente.

### 3. Configure o Ambiente Python
```bash
# Crie e ative o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
# ou se usar pyproject.toml:
pip install -e .
```

### 4. Configure as Variáveis de Ambiente
Copie o arquivo de exemplo e ajuste se necessário:
```bash
cp .env.example .env
```
O padrão aponta para o Docker Compose local:
```
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/financas_db
```

### 5. Execute as Migrações do Banco (Alembic)
```bash
alembic upgrade head
```
> Isso cria todas as tabelas: `categorias`, `receitas`, `despesas`, `importacoes`, `registros_rejeitados` e a view `vw_movimentacoes`.

---

## 🏃 Como Executar

### 1. Inicie o Dashboard (Streamlit)
```bash
streamlit run app/dashboard.py
```
O navegador abrirá automaticamente em `http://localhost:8501`.

### 2. Importe o Arquivo de Exemplo
1. No menu lateral, clique em **"Importar CSV"**.
2. Faça upload do arquivo `data/exemplo/extrato_teste.csv`.
3. Marque **"Criar categorias automaticamente se não existirem"**.
4. Clique em **"Iniciar Importação"**.
5. Verifique o resumo: linhas lidas, aceitas, rejeitadas e duplicadas.

### 3. Explore o Dashboard
Navegue pelas páginas no menu lateral:
- **Visão Geral**: KPIs do mês (Receitas, Despesas, Saldo, % Comprometido).
- **Gastos**: Gráficos e tabela por categoria com filtros de data.
- **Evolução**: Série temporal de saldo acumulado e comparação entre meses.
- **Recorrentes**: Detecção automática de despesas fixas (aluguel, assinaturas).
- **Categorias**: Cadastro, edição e ativação/desativação de categorias.

---

## 🧪 Testes e Qualidade

### Rodar Testes Automatizados
```bash
pytest
```
> Todos os testes devem passar (importação, categorias, validações).

### Verificar Estilo de Código (Linting)
```bash
ruff check .
```

---

## 📁 Estrutura do Projeto
```
financas-pessoais/
├── app/
│   └── dashboard.py          # Entrada principal do Streamlit
├── data/
│   └── exemplo/
│       └── extrato_teste.csv # CSV com 6 meses, casos de borda e recorrências
├── migrations/               # Migrações Alembic versionadas
├── sql/
│   └── analise/              # 6 Consultas SQL documentadas (.sql)
├── src/financas/
│   ├── banco.py              # Conexão e Sessão SQLAlchemy
│   ├── config.py             # Leitura de .env
│   ├── modelos.py            # Tabelas ORM (Decimal/NUMERIC para dinheiro)
│   ├── importacao/           # Leitura, normalização, validação e serviço
│   ├── categorias/           # CRUD de categorias
│   └── analise/              # Executor das consultas SQL
├── tests/                    # Testes unitários (pytest)
├── alembic.ini               # Configuração Alembic
├── docker-compose.yml        # PostgreSQL local
├── pyproject.toml            # Dependências e config ferramentas
├── .env.example              # Modelo de variáveis de ambiente
├── README.md                 # Este arquivo
├── design.md                 # Decisões de arquitetura e modelo
└── RELATORIO.md              # Diário de desenvolvimento por fase
```

---

## 💡 Regras de Negócio Implementadas
- **Dinheiro**: Sempre `Decimal` (Python) / `NUMERIC(12,2)` (Postgres). Nunca `float`.
- **Datas**: Armazenadas como `DATE`. Agregações mensais usam o 1º dia do mês.
- **Idempotência**: Reimportar o mesmo CSV não duplica dados (hash SHA-256).
- **Validação Rigorosa**: 7 regras (colunas, datas, valores > 0, tipo, descrição, categoria, duplicatas).
- **Rastreabilidade**: Linhas inválidas vão para `registros_rejeitados` com motivo.
- **Categorias**: Únicas por tipo (`receita`/`despesa`). Desativadas não somem do histórico.

---

## 🛠️ Comandos Úteis

| Ação | Comando |
|------|---------|
| Criar nova migração | `alembic revision --autogenerate -m "descrição"` |
| Ver histórico migrações | `alembic history` |
| Derrubar banco (cuidado!) | `docker-compose down -v` |
| Formatar código | `ruff check . --fix` |

---

## 📄 Licença
Uso educacional / pessoal.