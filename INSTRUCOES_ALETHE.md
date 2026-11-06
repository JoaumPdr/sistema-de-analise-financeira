# INSTRUÇÕES PARA A ALETHE — Sistema de Análise Financeira Pessoal

> Leia este arquivo inteiro antes de planejar ou delegar qualquer coisa. **A seção 0 (documentação, organização, branches e commits) é obrigatória e tem prioridade.**
> Em seguida, leia o playbook (`scripts/orchestrate.py playbook`) e siga as regras da seção 2.

---

## 0. LEIA PRIMEIRO — Documentação, organização, branches e commits

> Esta seção tem **prioridade** sobre qualquer outra instrução do arquivo.
> Vale para você e para todos os workers que você delegar. Inclua um resumo dela em todo briefing de worker que escreve código.

### 0.1 Documentação

**Idioma:** tudo em **PT-BR** (documentos, comentários, docstrings, mensagens de commit, nomes de branch e textos da interface).

**Três documentos vivos, mantidos durante o desenvolvimento, não só no fim:**

| Arquivo | Para que serve | Quando atualizar |
|---|---|---|
| `README.md` | Como instalar, configurar, importar um CSV, rodar o dashboard e rodar os testes | Sempre que algo mudar na instalação ou no uso |
| `design.md` | Arquitetura, modelo de dados e **decisões com justificativa** | Sempre que uma decisão técnica for tomada |
| `RELATORIO.md` | Diário do projeto, uma entrada por fase | Ao concluir cada fase (e ao encontrar um problema relevante) |

**Regras:**
1. **A documentação vai no mesmo commit (ou na mesma branch) da mudança que a motivou.** Nenhuma fase é considerada concluída com documentação desatualizada.
2. **`design.md` registra o porquê.** Para cada decisão relevante, escreva: o contexto, o que foi decidido, as alternativas consideradas e a consequência. Exemplo de decisão: usar `NUMERIC` em vez de `float` para dinheiro.
3. **`RELATORIO.md` é um registro cumulativo (não apague entradas antigas).** Cada fase tem: data, objetivo, o que foi feito, decisões tomadas, problemas encontrados e como foram resolvidos, testes executados, playbook e tier usados, e próximos passos.
4. **Comentários didáticos, para desenvolvedores iniciantes.** Explique o **porquê** das escolhas, não só o que a linha faz. Todo módulo Python começa com um comentário/docstring dizendo qual o seu papel no sistema. Toda função pública tem docstring com o que recebe, o que devolve e por que existe.
5. **Cada arquivo `.sql` começa com um cabeçalho** explicando o objetivo da consulta, os parâmetros e o formato do resultado.
6. **Sem documentação "fantasma":** não documente o que não existe e não deixe o README descrever comandos que não funcionam. O README deve ser testado seguindo seus próprios passos.

### 0.2 Organização do desenvolvimento

1. **Uma fase por vez, uma unidade por vez.** Antes de começar uma unidade, deixe claro: o objetivo, os arquivos que serão tocados e a verificação que prova que ficou pronta.
2. **Quadro de status no topo do `RELATORIO.md`:** liste F0 a F6 com o estado `pendente`, `em andamento` ou `concluída`, e mantenha atualizado.
3. **Definição de pronto de uma unidade:** o código funciona, os testes da unidade passam, o `ruff` passa, os comentários e docstrings estão escritos, a documentação foi atualizada e o diff passou pelo `review-gate` quando for unidade de risco.
4. **Não avance de fase** sem o critério de aceite verde (seção 9) e sem a entrada da fase registrada no `RELATORIO.md`.
5. **Sem mudanças escondidas:** cada commit trata de **uma coisa só**. Não misture refatoração, correção e funcionalidade nova. Se perceber algo fora do escopo, anote no `RELATORIO.md` como pendência em vez de mexer.
6. **Árvore de trabalho limpa** antes de iniciar uma nova unidade (nada pendente de commit da unidade anterior).
7. **Decisões que mudam o escopo** (dependência grande, formato do CSV, modelo de dados já aprovado) vão para mim antes. As demais você decide e registra no `design.md`.

### 0.3 Branches

- **Branch padrão** (`main`, ou `master` se o repositório já usar esse nome): sempre estável, testes passando. **Nunca commitar direto nela.**
- **Uma branch por unidade de trabalho**, criada a partir da branch padrão atualizada.
- **Nomes:** `tipo/descricao-curta`, em minúsculas, com hífens e sem acentos.
  - Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
  - Exemplos: `feat/modelo-de-dados`, `feat/importacao-csv`, `feat/consultas-analise`, `feat/dashboard-visao-geral`, `docs/readme-instalacao`, `fix/divisao-por-zero-renda`.
- **Fluxo de cada unidade:**
  1. Criar a branch a partir da branch padrão.
  2. Desenvolver em commits pequenos.
  3. Rodar testes e `ruff` (devem estar verdes).
  4. Passar pelo `review-gate` se for unidade de risco.
  5. Atualizar `design.md`, `README.md` e `RELATORIO.md` se forem afetados.
  6. Mesclar na branch padrão com merge que preserve o histórico da branch (`--no-ff`), com mensagem em PT-BR, e apagar a branch mesclada.
- **Ao concluir uma fase:** crie uma tag `fase-F<n>` (ex.: `fase-F2`) na branch padrão, para eu conseguir voltar a qualquer fase.
- **Trabalho paralelo (`parallel-worktrees`):** cada worker usa seu próprio worktree e sua própria branch, sem tocar nos arquivos dos outros. O integrador mescla uma por vez e roda a suíte de testes completa a cada merge.

### 0.4 Commits

**Formato (Conventional Commits em PT-BR):** `tipo(escopo): descrição`

- **Tipos:** `feat` (funcionalidade), `fix` (correção), `docs` (documentação), `test` (testes), `refactor` (reorganização sem mudar comportamento), `chore` (configuração e manutenção), `build` (dependências e empacotamento).
- **Escopo (opcional):** o módulo afetado, como `importacao`, `analise`, `dashboard`, `banco`, `categorias`.
- **Descrição:** no imperativo ou no infinitivo de forma consistente, em minúsculas, no máximo ~72 caracteres, sem ponto final.
- **Corpo (quando a mudança não for óbvia):** uma linha em branco e depois o **porquê** da mudança, não só o que mudou.

**Exemplos de mensagens boas:**
- `feat(importacao): valida data e valor ao ler o csv`
- `fix(analise): evita divisão por zero no percentual de renda comprometida`
- `docs(design): registra decisão de usar numeric para valores monetários`
- `test(importacao): cobre reimportação do mesmo arquivo sem duplicar`
- `chore(banco): adiciona docker compose do postgres`

**Regras:**
1. **Um commit = uma mudança lógica.** Commits pequenos e frequentes, nada de um commit gigante no fim da fase.
2. **O commit inclui o que a mudança precisa:** código, testes e a documentação correspondente.
3. **Nunca commitar:** `.env`, dados financeiros reais, CSVs reais, `.venv`, `__pycache__`, arquivos de cache e credenciais. Confira o `.gitignore` na F0.
4. **Nunca commitar com testes ou `ruff` falhando.**
5. **Proibido:** `--force` em branch compartilhada, reescrever histórico já mesclado e pular verificações (`--no-verify`).
6. **Mensagens de merge também em PT-BR**, por exemplo: `merge: conclui importação de csv (fase F2)`.

---

## 1. Objetivo

Construir um sistema que **importa receitas e despesas de arquivos CSV** e as transforma em **informações financeiras úteis**: gastos por categoria, médias mensais, comparação entre meses, despesas recorrentes e percentual de renda comprometida, tudo apresentado em um dashboard.

**Stack obrigatória:** Python, pandas, PostgreSQL, SQLAlchemy e Streamlit.
**Complementos permitidos (sem pedir autorização):** Alembic (migrações), pytest, ruff, Docker Compose (apenas para subir o PostgreSQL local), Plotly ou os gráficos nativos do Streamlit.
**Qualquer outra dependência nova:** justifique em uma linha no `design.md` antes de adicionar.

Referência visual de dashboard (apenas inspiração de layout, não copiar):
[Bank Statement Analytics — Arun G](https://images.openai.com/static-rsc-4/qKePD7ht3-mIzRTUfi_HCwQqG0GB0vAag7VNxX9_Lpj-LPUf3Ca_tm595X3qEl-KkQ6StSz7vTJ3knKsa0txL9XLSywVYV7zecECwUFZjR9apGMPZ843SRVailunwmRrKv4HShb9D0toug1PebexrBr7GKhSAxoPGzpTXJkydZE?purpose=inline)

---

## 2. Como orquestrar (regras vindas do `playbooks.yaml`)

Siga os princípios do playbook anexado. Em resumo prático para este projeto:

1. **Escolha o playbook por unidade de trabalho**, usando o `pickOrder`. Mapa sugerido por fase:

   | Fase | Playbook sugerido | Motivo |
   |---|---|---|
   | F0 — Estrutura inicial | `direct` | Tarefa estreita, poucos arquivos |
   | F1 — Modelo de dados | `plan-execute` | Decisão importante, depois execução em passos |
   | F2 — Importação e validação | `plan-execute` + `cascade` nos validadores | Cada regra tem teste automático |
   | F3 — Consultas SQL de análise | `plan-execute` | Consultas dependem do schema da F1 |
   | F4 — Categorias | `direct` | Módulo pequeno |
   | F5 — Dashboard | `plan-execute` | Depende das consultas da F3 |
   | F6 — Documentação e fechamento | `direct` + `review-gate` final | Revisão geral antes de entregar |

   F3 e F4 não compartilham arquivos depois que as interfaces estiverem fixadas; se o ganho de tempo valer a pena, use `parallel-worktrees` para elas. Caso contrário, siga em sequência.
2. **Fixe modelo e esforço de cada worker** na hora de delegar. Nunca deixe um worker rodar no modelo padrão da CLI.
3. **Camada forte para decidir, camada barata para volume.** Planejamento e decisões de schema ficam na camada `strong`; implementação na `standard`; leituras e triagens na `cheap`.
4. **Unidades de risco nunca rodam na camada `cheap`** e seus diffs passam por `review-gate`. Neste projeto, são de risco:
   - o schema do banco e as migrações;
   - as regras de validação dos registros;
   - o cálculo de dinheiro (somas, médias, percentuais);
   - a detecção de despesas recorrentes.
5. **Escale só quando uma verificação falhar** (teste, lint, checagem de tipos), nunca porque o worker disse que terminou. Um nível por vez, uma vez por unidade.
6. **Revise apenas diffs finalizados**, nunca trabalho em andamento. Todo playbook que escreve código termina em `review-gate`.
7. **Mantenha seu contexto pequeno:** peça aos workers respostas, evidências e diffs, nunca transcrições.
8. **Respeite o orçamento e a cota** configurados (`budget.warnAt`, `quota`). Se o orçamento ficar baixo, termine a unidade atual e me reporte antes de seguir.
9. **Perfil ativo:** `base`, a menos que eu peça outro.

---

## 3. Regras gerais do projeto

- **Idioma:** toda documentação, mensagens de commit, nomes de tabelas/colunas e textos da interface em **PT-BR**. Nomes de variáveis e funções em Python podem seguir o padrão do código, desde que sejam consistentes em todo o projeto.
- **Comentários didáticos:** escreva comentários e docstrings acessíveis para desenvolvedores iniciantes, explicando **o porquê** das decisões, não só o que o código faz.
- **Dinheiro:** nunca use `float`. Use `Decimal` em Python e `NUMERIC(12,2)` no PostgreSQL.
- **Datas:** armazene como `DATE`. Agregações mensais usam o primeiro dia do mês como chave.
- **Segredos:** a conexão com o banco vem de variáveis de ambiente (`.env`, com `.env.example` versionado e `.env` no `.gitignore`).
- **Documentação, branches e commits:** siga a seção 0, que tem prioridade sobre qualquer outra instrução deste arquivo.
- **Sem dados reais no repositório.** Use apenas o CSV de exemplo fictício.
- **Teste antes de declarar pronto.** Nenhuma unidade está concluída sem seus testes passando.

---

## 4. Estrutura de pastas esperada

```
financas-pessoais/
├── README.md              # como instalar, configurar e rodar
├── RELATORIO.md           # o que foi feito, decisões, problemas e resultados por fase
├── design.md              # arquitetura, modelo de dados e justificativas
├── .env.example
├── docker-compose.yml     # somente o PostgreSQL local
├── pyproject.toml         # ou requirements.txt
├── migrations/            # Alembic
├── sql/
│   └── analise/           # uma consulta por arquivo .sql, documentada no topo
├── src/financas/
│   ├── config.py          # leitura de variáveis de ambiente
│   ├── banco.py           # engine e sessão do SQLAlchemy
│   ├── modelos.py         # tabelas (ORM)
│   ├── importacao/        # leitura do CSV, normalização e validação
│   ├── categorias/        # cadastro e regras de categoria
│   └── analise/           # funções que executam as consultas de sql/analise
├── app/
│   ├── dashboard.py       # entrada do Streamlit
│   └── paginas/           # importação, categorias, análises
├── tests/
└── data/exemplo/          # CSV fictício para testes e demonstração
```

Se precisar mudar essa estrutura, registre o motivo no `design.md`.

---

## 5. Modelo de dados (a ser refinado e fixado na F1)

Banco relacional com **tabelas separadas para receitas, despesas e categorias**, como pedido.

| Tabela | Campos principais | Regras |
|---|---|---|
| `categorias` | id, nome, tipo (`receita` ou `despesa`), ativa, criada_em | Nome único por tipo |
| `receitas` | id, data, descricao, valor, categoria_id, importacao_id, hash_registro | Valor > 0; `hash_registro` único (evita duplicar ao reimportar) |
| `despesas` | id, data, descricao, valor, categoria_id, importacao_id, hash_registro | Valor > 0; `hash_registro` único |
| `importacoes` | id, nome_arquivo, hash_arquivo, importada_em, linhas_lidas, linhas_aceitas, linhas_rejeitadas | Registra cada arquivo importado |
| `registros_rejeitados` | id, importacao_id, numero_linha, motivo, conteudo_bruto | Nada é descartado em silêncio |

Extras esperados:
- Chaves estrangeiras e índices em `data` e `categoria_id`.
- Uma **view** `vw_movimentacoes` unindo receitas e despesas (com coluna `tipo`) para facilitar as consultas de evolução.
- Migrações Alembic versionadas; nada de criar tabelas "na mão".

---

## 6. Importação e validação de CSV

**Colunas esperadas:** `data`, `descricao`, `valor`, `tipo` (`receita` ou `despesa`), `categoria`.

**Tolerâncias na leitura:**
- Separador `,` ou `;` (detectar automaticamente).
- Codificação UTF-8 com fallback para Latin-1.
- Datas em `DD/MM/AAAA` ou `AAAA-MM-DD`.
- Valores com vírgula decimal (`1.234,56`) ou ponto decimal.

**Regras de validação (cada uma com teste próprio):**
1. Todas as colunas obrigatórias presentes; caso contrário, o arquivo é recusado com mensagem clara.
2. Data válida e não absurda (não futura além de um limite configurável).
3. Valor numérico e maior que zero (o sinal vem do campo `tipo`).
4. `tipo` apenas `receita` ou `despesa`.
5. Descrição não vazia, com espaços extras removidos.
6. Categoria existente; se não existir, criar automaticamente **somente** quando a opção estiver ligada, senão rejeitar a linha.
7. Duplicata detectada pelo `hash_registro` (data + descrição normalizada + valor + tipo); duplicatas são contadas e relatadas, não inseridas.

**Comportamento esperado:**
- Linhas inválidas vão para `registros_rejeitados` com o motivo; as válidas são inseridas.
- A importação de um arquivo é **transacional**: se algo inesperado quebrar no meio, nada fica pela metade.
- Reimportar o mesmo arquivo não pode duplicar dados.
- Ao final, devolver um resumo: lidas, aceitas, rejeitadas, duplicadas.

Crie um CSV fictício em `data/exemplo/` com pelo menos 6 meses de dados, incluindo de propósito: linhas inválidas, uma duplicata, despesas recorrentes (aluguel, assinaturas, internet) e um mês sem receita.

---

## 7. Consultas SQL de análise

Cada consulta fica em um arquivo `.sql` em `sql/analise/`, com um cabeçalho explicando o objetivo, os parâmetros e o formato do resultado. São executadas via SQLAlchemy com parâmetros (nunca concatenando texto).

| # | Consulta | O que deve retornar |
|---|---|---|
| 1 | **Gastos por categoria** | Total por categoria em um período, com percentual sobre o total de despesas |
| 2 | **Média de despesas mensais** | Média dos últimos N meses, no geral e por categoria |
| 3 | **Comparação entre meses** | Mês escolhido contra o anterior, por categoria: valor, diferença absoluta e variação percentual |
| 4 | **Despesas recorrentes** | Despesas com descrição normalizada parecida e valor próximo (tolerância configurável, ex.: ±10%) em pelo menos 3 meses distintos, com o valor médio e o total mensal comprometido |
| 5 | **Percentual de renda comprometida** | Por mês: despesas ÷ receitas × 100 |
| 6 | **Evolução financeira** | Por mês: receitas, despesas, saldo e saldo acumulado |

**Casos de borda obrigatórios:**
- Mês sem receita: o percentual da consulta 5 deve retornar vazio (`NULL`), nunca dividir por zero.
- Mês anterior inexistente na consulta 3: mostrar a variação como indisponível.
- Período sem dados: retornar resultado vazio, não erro.

**Testes:** use um conjunto pequeno e fixo de dados de teste onde o resultado esperado de cada consulta seja calculável à mão e conferido no teste.

---

## 8. Dashboard (Streamlit)

**Páginas:**
1. **Visão geral:** cartões com receita do mês, despesa do mês, saldo e % de renda comprometida.
2. **Gastos:** gráfico de gastos por categoria e tabela detalhada, com filtro de período e de categorias.
3. **Evolução:** gráfico de receitas, despesas e saldo ao longo dos meses e comparação entre dois meses.
4. **Recorrentes:** tabela de despesas recorrentes e o total mensal que elas representam.
5. **Importar:** upload do CSV, resumo da importação e lista das linhas rejeitadas com o motivo.
6. **Categorias:** cadastro, edição e desativação de categorias.

**Requisitos:**
- Os dados vêm das funções da pasta `analise/`, nunca de SQL escrito dentro das páginas.
- Valores exibidos em reais (`R$ 1.234,56`) e datas em `DD/MM/AAAA`.
- Estados vazios tratados com mensagem amigável (banco sem dados, filtro sem resultado).
- Layout legível também em tela estreita (mobile-first), sem tabelas largas que estourem a tela.
- Cache do Streamlit apenas onde fizer sentido, e invalidado após uma nova importação.

---

## 9. Fases, entregas e critérios de aceite

Execute em ordem. **Só avance quando o critério de aceite da fase estiver verde** e o diff tiver passado pelo `review-gate`.

### F0 — Estrutura inicial
- Criar pastas, `pyproject.toml`/`requirements.txt`, `.env.example`, `.gitignore`, `docker-compose.yml` (PostgreSQL) e esqueletos de `README.md`, `RELATORIO.md`, `design.md`.
- Inicializar o repositório Git (se ainda não existir), configurar o `.gitignore` conforme a seção 0.4, fazer o commit inicial na branch padrão e criar o quadro de status das fases no `RELATORIO.md`.
- **Aceite:** o banco sobe com Docker Compose, a conexão funciona, `pytest` e `ruff` rodam (mesmo sem testes ainda), e o repositório segue as convenções de branch e commit da seção 0.

### F1 — Modelo de dados
- Definir o schema da seção 5 em `modelos.py` e gerar a migração inicial.
- Documentar o modelo e as decisões no `design.md`.
- **Aceite:** a migração sobe e desfaz sem erro; restrições (valor > 0, hash único, chaves estrangeiras) comprovadas por testes.

### F2 — Importação e validação
- Implementar a seção 6 completa, mais o CSV de exemplo.
- **Aceite:** cada regra de validação tem teste; reimportar o mesmo arquivo não duplica; o resumo da importação confere com o CSV de exemplo.

### F3 — Consultas SQL de análise
- Implementar as 6 consultas da seção 7 e as funções que as executam.
- **Aceite:** testes com resultado conferido à mão para cada consulta e para os casos de borda.

### F4 — Categorias
- Cadastro, edição, desativação e listagem; categoria desativada não aparece para novos registros, mas continua nos históricos.
- **Aceite:** testes de criação, duplicidade de nome e desativação.

### F5 — Dashboard
- Implementar as páginas da seção 8 usando apenas as funções da F3 e da F4.
- **Aceite:** o app abre com o CSV de exemplo importado, todas as páginas carregam sem erro e os números batem com os testes da F3.

### F6 — Documentação e fechamento
- Completar `README.md` (instalação, configuração, como importar e como rodar o dashboard), `design.md` e `RELATORIO.md` (o que foi feito por fase, decisões, problemas e como foram resolvidos).
- Rodar uma revisão completa (`review-gate`) sobre todo o projeto.
- **Aceite:** um desenvolvedor iniciante consegue seguir o README do zero e ver o dashboard funcionando.

---

## 10. Como me reportar

- Ao fim de cada fase, envie um resumo curto: o que foi feito, testes executados, riscos e o playbook/tier usado.
- Se uma verificação falhar duas vezes na mesma unidade, pare e me explique o problema em vez de insistir.
- Se precisar tomar uma decisão que muda o escopo (nova dependência grande, mudar o formato do CSV, mudar o modelo de dados já aprovado), **pergunte antes**.
- Para todo o resto, decida com base neste documento e registre a decisão no `design.md`.

## 11. Suposições adotadas (podem ser alteradas por mim a qualquer momento)

- Uso individual, um único usuário, sem login.
- O CSV segue as colunas da seção 6; se meu extrato real tiver outro formato (por exemplo, valor negativo para despesa), tratar como uma melhoria futura configurável, e não bloquear o início.
- Moeda única: real (BRL).
- Execução local, com o PostgreSQL via Docker Compose.

## 12. Primeira ação

1. Leia o playbook e confirme o perfil ativo e os limites de orçamento.
2. Verifique se Docker e Python estão disponíveis no ambiente; se não estiverem, me avise antes de seguir.
3. Releia a seção 0 e confirme que vai seguir as regras de documentação, branches e commits.
4. Crie a branch da F0 (`chore/estrutura-inicial`) e inicie a **F0** com o playbook `direct`.
