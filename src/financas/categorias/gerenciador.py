from sqlalchemy.orm import Session
from sqlalchemy import text
from src.financas.modelos import Categoria
from typing import List, Dict, Any, Optional

class GerenciadorCategorias:
    """
    Responsável pela gestão do ciclo de vida das categorias financeiras.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def listar_categorias(self, apenas_ativas: bool = True) -> List[Dict[str, Any]]:
        """
        Lista categorias. Se apenas_ativas=True, omite as desativadas.
        """
        query = "SELECT id, nome, tipo, ativa FROM categorias"
        if apenas_ativas:
            query += " WHERE ativa = true"
        
        res = self.session.execute(text(query)).fetchall()
        return [
            {"id": row[0], "nome": row[1], "tipo": row[2], "ativa": row[3]} 
            for row in res
        ]

    def criar_categoria(self, nome: str, tipo: str) -> Optional[Categoria]:
        """
        Cria uma nova categoria. 
        Valida se já existe uma categoria com o mesmo nome para o mesmo tipo.
        """
        nome_limpo = nome.strip()
        tipo_limpo = tipo.strip().lower()
        
        if tipo_limpo not in ('receita', 'despesa'):
            raise ValueError("O tipo deve ser 'receita' ou 'despesa'.")

        # Verificar duplicidade
        existe = self.session.execute(
            text("SELECT 1 FROM categorias WHERE nome = :n AND tipo = :t"),
            {"n": nome_limpo, "t": tipo_limpo}
        ).fetchone()
        
        if existe:
            return None # Categoria já existe
            
        nova_cat = Categoria(nome=nome_limpo, tipo=tipo_limpo)
        self.session.add(nova_cat)
        self.session.commit()
        return nova_cat

    def editar_categoria(self, categoria_id: int, novo_nome: str) -> bool:
        """
        Edita o nome de uma categoria.
        """
        nome_limpo = novo_nome.strip()
        
        # Verificar se o novo nome já é usado por outra categoria do mesmo tipo
        cat = self.session.get(Categoria, categoria_id)
        if not cat:
            return False
            
        existe = self.session.execute(
            text("SELECT 1 FROM categorias WHERE nome = :n AND tipo = :t AND id != :id"),
            {"n": nome_limpo, "t": cat.tipo, "id": categoria_id}
        ).fetchone()
        
        if existe:
            return False
            
        cat.nome = nome_limpo
        self.session.commit()
        return True

    def alternar_status(self, categoria_id: int, ativa: bool) -> bool:
        """
        Ativa ou desativa uma categoria.
        """
        cat = self.session.get(Categoria, categoria_id)
        if not cat:
            return False
            
        cat.ativa = ativa
        self.session.commit()
        return True
