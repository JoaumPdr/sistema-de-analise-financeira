-- Objetivo: Identificar despesas recorrentes baseadas na descrição normalizada e valor aproximado.
-- Parâmetros:
--   - tolerancia: Percentual de variação aceito para o valor (ex: 0.10 para +/- 10%).
-- Formato de retorno:
--   - descricao: Descrição da despesa recorrente.
--   - categoria: Categoria associada.
--   - valor_medio: Valor médio das ocorrências.
--   - meses_distintos: Quantidade de meses únicos em que a despesa ocorreu.
--   - total_mensal_comprometido: Estimativa do valor mensal total gasto com essa recorrência.

WITH despesas_normalizadas AS (
    SELECT 
        d.descricao,
        c.nome AS categoria,
        d.valor,
        DATE_TRUNC('month', d.data)::DATE AS mes
    FROM despesas d
    JOIN categorias c ON d.categoria_id = c.id
),
agrupado AS (
    SELECT 
        descricao,
        categoria,
        AVG(valor) AS valor_medio,
        COUNT(DISTINCT mes) AS meses_distintos
    FROM despesas_normalizadas
    GROUP BY descricao, categoria
    HAVING COUNT(DISTINCT mes) >= 3
)
SELECT 
    descricao,
    categoria,
    ROUND(valor_medio, 2) AS valor_medio,
    meses_distintos,
    ROUND(valor_medio, 2) AS total_mensal_comprometido
FROM agrupado
ORDER BY total_mensal_comprometido DESC;
