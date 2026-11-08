from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'receita' ou 'despesa'
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime, default=datetime.utcnow)

    # Nome único por tipo para evitar duplicados
    __table_args__ = (Index("idx_categoria_nome_tipo", "nome", "tipo", unique=True),)


class Importacao(Base):
    __tablename__ = "importacoes"

    id = Column(Integer, primary_key=True)
    nome_arquivo = Column(String(255), nullable=False)
    hash_arquivo = Column(
        String(64), nullable=False
    )  # SHA-256 para evitar re-processar mesmo arquivo
    importada_em = Column(DateTime, default=datetime.utcnow)
    linhas_lidas = Column(Integer, default=0)
    linhas_aceitas = Column(Integer, default=0)
    linhas_rejeitadas = Column(Integer, default=0)


class RegistroRejeitado(Base):
    __tablename__ = "registros_rejeitados"

    id = Column(Integer, primary_key=True)
    importacao_id = Column(Integer, ForeignKey("importacoes.id"), nullable=False)
    numero_linha = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=False)
    conteudo_bruto = Column(String, nullable=False)


class Receita(Base):
    __tablename__ = "receitas"

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    importacao_id = Column(Integer, ForeignKey("importacoes.id"), nullable=False)
    hash_registro = Column(
        String(64), nullable=False, unique=True
    )  # data + desc + valor + tipo

    categoria = relationship("Categoria")


class Despesa(Base):
    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    importacao_id = Column(Integer, ForeignKey("importacoes.id"), nullable=False)
    hash_registro = Column(
        String(64), nullable=False, unique=True
    )  # data + desc + valor + tipo

    categoria = relationship("Categoria")


# View vw_movimentacoes será criada via migração Alembic usando SQL puro
