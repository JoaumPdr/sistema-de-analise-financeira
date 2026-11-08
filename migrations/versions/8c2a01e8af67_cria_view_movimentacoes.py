"""cria_view_movimentacoes

Revision ID: 8c2a01e8af67
Revises: 615a9cda8c5b
Create Date: 2026-11-07 20:53:47.165198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c2a01e8af67'
down_revision: Union[str, Sequence[str], None] = '615a9cda8c5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE VIEW vw_movimentacoes AS
        SELECT 
            id, data, descricao, valor, 'receita' AS tipo, categoria_id, importacao_id, hash_registro 
        FROM receitas
        UNION ALL
        SELECT 
            id, data, descricao, valor, 'despesa' AS tipo, categoria_id, importacao_id, hash_registro 
        FROM despesas;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS vw_movimentacoes;")
