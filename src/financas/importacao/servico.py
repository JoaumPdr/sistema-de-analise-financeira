import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.financas.modelos import Importacao, Receita, Despesa, RegistroRejeitado, Categoria
from src.financas.importacao.normalizadores import detectar_configuracao_csv, normalizar_valor, normalizar_data, calcular_hash
from src.financas.importacao.validador import ValidadorImportacao
from typing import Dict, Any

class ServicoImportacao:
    """
    Orquestra a importação de arquivos CSV para o banco de dados.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def _obter_categorias_existentes(self) -> set:
        # Busca apenas nomes de categorias ativas
        res = self.session.execute(text("SELECT nome FROM categorias WHERE ativa = true")).fetchall()
        return {row[0] for row in res}

    def importar_csv(self, caminho_arquivo: str, criar_categorias: bool = False) -> Dict[str, Any]:
        # 1. Detectar Configuração
        cod, sep = detectar_configuracao_csv(caminho_arquivo)
        df = pd.read_csv(caminho_arquivo, sep=sep, encoding=cod)
        
        # 2. Preparar Importação no Banco
        # Gerar hash do arquivo para evitar re-processar o mesmo arquivo exatamente igual
        with open(caminho_arquivo, 'rb') as f:
            import hashlib
            hash_arquivo = hashlib.sha256(f.read()).hexdigest()
            
        importacao = Importacao(
            nome_arquivo=caminho_arquivo,
            hash_arquivo=hash_arquivo,
            linhas_lidas=len(df)
        )
        self.session.add(importacao)
        self.session.flush() # Gera o ID da importação

        # 3. Validação e Processamento
        categorias_atuais = self._obter_categorias_existentes()
        validador = ValidadorImportacao(categorias_atuais, criar_categorias_automaticamente=criar_categorias)
        
        aceitos = 0
        rejeitados = 0
        duplicados = 0
        
        try:
            for idx, row in df.iterrows():
                linha_dict = row.to_dict()
                valido, motivo = validador.validar_linha(linha_dict)
                
                if not valido:
                    # Registrar rejeitado
                    rejeitado = RegistroRejeitado(
                        importacao_id=importacao.id,
                        numero_linha=idx + 2, # +2 por causa do header e index 0
                        motivo=motivo,
                        conteudo_bruto=str(row.values)
                    )
                    self.session.add(rejeitado)
                    rejeitados += 1
                    continue
                
                # Normalizar para salvar
                data = normalizar_data(linha_dict['data'])
                valor = normalizar_valor(linha_dict['valor'])
                tipo = str(linha_dict['tipo']).strip().lower()
                descricao = str(linha_dict['descricao']).strip()
                categoria_nome = str(linha_dict['categoria']).strip()
                
                # Calcular hash do registro para evitar duplicatas
                h_reg = calcular_hash(data, descricao, valor, tipo)
                
                # Verificar duplicata
                exists = self.session.execute(
                    text("SELECT 1 FROM receitas WHERE hash_registro = :h UNION SELECT 1 FROM despesas WHERE hash_registro = :h"),
                    {"h": h_reg}
                ).fetchone()
                
                if exists:
                    duplicados += 1
                    continue
                
                # Resolver Categoria
                cat_id = None
                # Busca ID da categoria
                cat_row = self.session.execute(
                    text("SELECT id FROM categorias WHERE nome = :n AND tipo = :t"),
                    {"n": categoria_nome, "t": tipo}
                ).fetchone()
                
                if cat_row:
                    cat_id = cat_row[0]
                elif criar_categorias:
                    nova_cat = Categoria(nome=categoria_nome, tipo=tipo)
                    self.session.add(nova_cat)
                    self.session.flush()
                    cat_id = nova_cat.id
                
                # Inserir registro
                if tipo == 'receita':
                    reg = Receita(data=data, descricao=descricao, valor=valor, categoria_id=cat_id, importacao_id=importacao.id, hash_registro=h_reg)
                else:
                    reg = Despesa(data=data, descricao=descricao, valor=valor, categoria_id=cat_id, importacao_id=importacao.id, hash_registro=h_reg)
                
                self.session.add(reg)
                aceitos += 1
            
            # Atualizar resumo da importação
            importacao.linhas_aceitas = aceitos
            importacao.linhas_rejeitadas = rejeitados
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise e

        return {
            "lidas": len(df),
            "aceitas": aceitos,
            "rejeitadas": rejeitados,
            "duplicadas": duplicados
        }
