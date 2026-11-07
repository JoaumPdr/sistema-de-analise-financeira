-- Objetivo: Calcular o total de gastos por categoria em um período e seu percentual sobre o total de despesas.
-- Parâmetros: :data_inicio, :data_fim
-- Resultado: nome_categoria, total, percentual

WITH total_periodo AS (
    SELECT SUM(valor) as total_geral 
    FROM despesas 
    WHERE data BETWEEN :data_inicio AND :data_fim
)
SELECT 
    c.nome as nome_categoria, 
    SUM(d.valor) as total, 
    (SUM(d.valor) / NULLIF(tp.total_geral, 0)) * 100 as percentual
FROM despesas d
JOIN categorias c ON d.categoria_id = c.id
CROSS JOIN total_periodo tp
WHERE d.data BETWEEN :data_inicio AND :data_fim
GROUP BY c.nome, tp.total_geral
ORDER BY total DESC;
