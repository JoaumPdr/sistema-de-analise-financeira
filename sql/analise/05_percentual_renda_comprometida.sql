-- Objetivo: Calcular o percentual de renda comprometida por mês (Despesas / Receitas * 100).
-- Parâmetros:
--   Nenhum (retorna a série histórica mensal).
-- Formato de retorno:
--   - mes: O mês correspondente (formato DATE).
--   - total_receitas: Soma das receitas do mês.
--   - total_despesas: Soma das despesas do mês.
--   - percentual_comprometido: (despesas / receitas) * 100 (Retorna NULL se receitas = 0).

WITH movimentacoes_mensais AS (
    SELECT 
        DATE_TRUNC('month', data)::DATE AS mes,
        SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0.00 END) AS total_receitas,
        SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0.00 END) AS total_despesas
    FROM vw_movimentacoes
    GROUP BY DATE_TRUNC('month', data)
)
SELECT 
    mes,
    total_receitas,
    total_despesas,
    CASE 
        WHEN total_receitas = 0 THEN NULL
        ELSE ROUND((total_despesas / total_receitas) * 100, 2)
    END AS percentual_comprometido
FROM movimentacoes_mensais
ORDER BY mes ASC;
