import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any

class AnalisadorFinanceiro:
    """
    Executa consultas SQL de análise e retorna os resultados formatados.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.sql_dir = "sql/analise"

    def _executar_sql(self, arquivo_sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        caminho = os.path.join(self.sql_dir, arquivo_sql)
        with open(caminho, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        result = self.session.execute(text(sql), params)
        # Converte as linhas do SQLAlchemy para dicionários
        return [row._asdict() for row in result]

    def gastos_por_categoria(self, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
        """Consulta 1: Total e percentual por categoria."""
        return self._executar_sql("01_gastos_por_categoria.sql", {
            "data_inicio": data_inicio, 
            "data_fim": data_fim
        })

    def media_despesas_mensais(self, meses_limite: int = 6) -> List[Dict[str, Any]]:
        """Consulta 2: Média de gastos por categoria nos últimos N meses."""
        return self._executar_sql("02_media_despesas_mensais.sql", {
            "meses_limite": meses_limite
        })
