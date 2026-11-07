-- Objetivo: Unificar receitas e despesas em uma única visão para análise de evolução financeira.
-- Parâmetros: Nenhum.
-- Resultado: id, data, descricao, valor, tipo (receita/despesa), categoria_id, importacao_id, hash_registro.

CREATE OR REPLACE VIEW vw_movimentacoes AS
SELECT 
    id, 
    data, 
    descricao, 
    valor, 
    'receita' AS tipo, 
    categoria_id, 
    importacao_id, 
    hash_registro 
FROM receitas
UNION ALL
SELECT 
    id, 
    data, 
    descricao, 
    valor, 
    'despesa' AS tipo, 
    categoria_id, 
    importacao_id, 
    hash_registro 
FROM despesas;
