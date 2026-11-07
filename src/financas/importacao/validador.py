from datetime import date
from typing import Any

from src.financas.importacao.normalizadores import normalizar_data, normalizar_valor


class ValidadorImportacao:
    """
    Implementa as 7 regras de validação da Seção 6 das instruções.
    """
    
    def __init__(self, categorias_existentes: set, criar_categorias_automaticamente: bool = False):
        self.categorias_existentes = categorias_existentes
        self.criar_categorias_automaticamente = criar_categorias_automaticamente

    def validar_linha(self, linha: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Valida uma linha de importação. 
        Retorna (True, None) se for válida, ou (False, "motivo") se for inválida.
        """
        # 1. Colunas obrigatórias
        for col in ['data', 'descricao', 'valor', 'tipo', 'categoria']:
            val = linha.get(col)
            if pd.isna(val) or str(val).strip() == "":
                return False, f"Coluna obrigatória {col} ausente ou vazia"

        # Normalização
        data = normalizar_data(linha['data'])
        valor = normalizar_valor(linha['valor'])
        tipo = str(linha['tipo']).strip().lower()
        descricao = str(linha['descricao']).strip()
        categoria = str(linha['categoria']).strip()

        # 2. Data válida e não absurda (limite: 2 anos no futuro)
        if data is None:
            return False, "Data em formato inválido"
        
        hoje = date.today()
        if data > hoje.replace(year=hoje.year + 2):
            return False, "Data excessivamente futura"

        # 3. Valor numérico e maior que zero
        if valor is None:
            return False, "Valor numérico inválido"
        if valor <= 0:
            return False, "Valor deve ser maior que zero (sinal definido pelo tipo)"

        # 4. Tipo apenas 'receita' ou 'despesa'
        if tipo not in ('receita', 'despesa'):
            return False, "Tipo deve ser 'receita' ou 'despesa'"

        # 5. Descrição não vazia
        if not descricao:
            return False, "Descrição não pode estar vazia"

        # 6. Categoria existente
        if categoria not in self.categorias_existentes and not self.criar_categorias_automaticamente:
            return False, f"Categoria '{categoria}' não cadastrada"
        
        return True, None

import pandas as pd
