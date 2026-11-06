-- Objetivo: Calcular a média de despesas mensais dos últimos N meses.
-- Parâmetros: :meses_limite (inteiro, ex: 6)
-- Resultado: nome_categoria, media_mensal

WITH mensal AS (
    SELECT 
        categoria_id, 
        DATE_TRUNC('month', data) as mes, 
        SUM(valor) as total_mes
    FROM despesas
    WHERE data >= CURRENT_DATE - INTERVAL '1 month' * :meses_limite
    GROUP BY categoria_id, DATE_TRUNC('month', data)
)
SELECT 
    c.nome as nome_categoria, 
    AVG(m.total_mes) as media_mensal
FROM mensal m
JOIN categorias c ON m.categoria_id = c.id
GROUP BY c.nome
ORDER BY media_mensal DESC;
