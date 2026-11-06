-- Objetivo: Calcular a evolução financeira mensal (receitas, despesas, saldo e saldo acumulado).
-- Parâmetros: Nenhum.
-- Resultado: mes, receitas, despesas, saldo, saldo_acumulado.

WITH mensal AS (
    SELECT 
        DATE_TRUNC('month', data)::DATE AS mes,
        SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0.00 END) AS receitas,
        SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0.00 END) AS despesas
    FROM vw_movimentacoes
    GROUP BY DATE_TRUNC('month', data)
),
calculos AS (
    SELECT 
        mes,
        receitas,
        despesas,
        (receitas - despesas) AS saldo
    FROM mensal
)
SELECT 
    mes,
    receitas,
    despesas,
    saldo,
    SUM(saldo) OVER (ORDER BY mes ASC) AS saldo_acumulado
FROM calculos
ORDER BY mes ASC;
