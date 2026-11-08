import os
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class AnalisadorFinanceiro:
    """
    Executa consultas SQL de análise e retorna os resultados formatados.
    """

    def __init__(self, session: Session):
        self.session = session
        self.sql_dir = "sql/analise"

    def _executar_sql(
        self, arquivo_sql: str, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        caminho = os.path.join(self.sql_dir, arquivo_sql)
        with open(caminho, "r", encoding="utf-8") as f:
            sql = f.read()

        result = self.session.execute(text(sql), params)
        # Converte as linhas do SQLAlchemy para dicionários
        return [row._asdict() for row in result]

    def gastos_por_categoria(
        self, data_inicio: str, data_fim: str
    ) -> list[dict[str, Any]]:
        """Consulta 1: Total e percentual por categoria."""
        return self._executar_sql(
            "01_gastos_por_categoria.sql",
            {"data_inicio": data_inicio, "data_fim": data_fim},
        )

    def comparacao_meses(self, mes_referencia: str) -> list[dict[str, Any]]:
        """Consulta 3: Comparação entre mês atual e anterior."""
        return self._executar_sql(
            "03_comparacao_entre_meses.sql", {"mes_referencia": mes_referencia}
        )

    def despesas_recorrentes(self, tolerancia: float = 0.10) -> list[dict[str, Any]]:
        """Consulta 4: Despesas recorrentes (descrição similar e valor próximo)."""
        return self._executar_sql(
            "04_despesas_recorrentes.sql", {"tolerancia": tolerancia}
        )

    def renda_comprometida(self) -> list[dict[str, Any]]:
        """Consulta 5: Percentual de renda comprometida por mês."""
        return self._executar_sql("05_percentual_renda_comprometida.sql", {})

    def evolucao_financeira(self) -> list[dict[str, Any]]:
        """Consulta 6: Evolução mensal de receitas, despesas e saldo acumulado."""
        return self._executar_sql("06_evolucao_financeira.sql", {})
