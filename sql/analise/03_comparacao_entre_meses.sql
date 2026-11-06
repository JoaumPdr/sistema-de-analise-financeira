-- Objetivo: Comparar os gastos por categoria entre um mês de referência e o mês anterior.
-- Parâmetros:
--   - mes_referencia: O mês base para a comparação (formato DATE, ex: '2026-05-01').
-- Formato de retorno:
--   - categoria: Nome da categoria de despesa.
--   - valor_atual: Valor total gasto no mês de referência.
--   - valor_anterior: Valor total gasto no mês anterior.
--   - diferenca_absoluta: valor_atual - valor_anterior.
--   - variacao_percentual: Percentual de variação entre os meses (tratando divisão por zero e inexistência do mês anterior).

WITH despesas_mensais AS (
    SELECT 
        c.nome AS categoria,
        DATE_TRUNC('month', d.data)::DATE AS mes,
        SUM(d.valor) AS total
    FROM despesas d
    JOIN categorias c ON d.categoria_id = c.id
    WHERE DATE_TRUNC('month', d.data) IN (
        (:mes_referencia)::DATE, 
        ((:mes_referencia)::DATE - INTERVAL '1 month')::DATE
    )
    GROUP BY c.nome, DATE_TRUNC('month', d.data)
)
SELECT 
    COALESCE(atual.categoria, anterior.categoria) AS categoria,
    COALESCE(atual.total, 0.00) AS valor_atual,
    COALESCE(anterior.total, 0.00) AS valor_anterior,
    (COALESCE(atual.total, 0.00) - COALESCE(anterior.total, 0.00)) AS diferenca_absoluta,
    CASE 
        WHEN COALESCE(anterior.total, 0.00) = 0 THEN NULL
        ELSE ROUND(((COALESCE(atual.total, 0.00) - anterior.total) / anterior.total) * 100, 2)
    END AS variacao_percentual
FROM (
    SELECT categoria, total 
    FROM despesas_mensais 
    WHERE mes = (:mes_referencia)::DATE
) atual
FULL OUTER JOIN (
    SELECT categoria, total 
    FROM despesas_mensais 
    WHERE mes = ((:mes_referencia)::DATE - INTERVAL '1 month')::DATE
) anterior ON atual.categoria = anterior.categoria
ORDER BY valor_atual DESC;
