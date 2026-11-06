import os
from decimal import Decimal, InvalidOperation
from datetime import datetime
import pandas as pd
import hashlib

class ImportacaoError(Exception):
    """Erro genérico de importação."""
    pass

def normalizar_valor(valor_str):
    """
    Converte strings de valor (ex: '1.234,56' ou '1234.56') para Decimal.
    """
    if pd.isna(valor_str) or str(valor_str).strip() == "":
        return None
    
    s = str(valor_str).strip()
    # Se tiver vírgula e ponto, assume-se formato brasileiro (1.234,56)
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    # Se tiver apenas vírgula, assume-se formato brasileiro (1234,56)
    elif ',' in s:
        s = s.replace(',', '.')
        
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def normalizar_data(data_str):
    """
    Tenta converter datas em DD/MM/AAAA ou AAAA-MM-DD.
    """
    if pd.isna(data_str) or str(data_str).strip() == "":
        return None
    
    s = str(data_str).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def calcular_hash(data, descricao, valor, tipo):
    """
    Gera um hash único para o registro para evitar duplicatas.
    """
    # Normalização simples da descrição: minúsculo e sem espaços extras
    desc_norm = str(descricao).strip().lower()
    payload = f"{data}|{desc_norm}|{valor}|{tipo}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def detectar_configuracao_csv(caminho_arquivo):
    """
    Detecta automaticamente o separador e a codificação do arquivo CSV.
    """
    codificacoes = ['utf-8', 'latin-1']
    separadores = [',', ';']
    
    for cod in codificacoes:
        try:
            with open(caminho_arquivo, 'r', encoding=cod) as f:
                primeira_linha = f.readline()
                if not primeira_linha:
                    continue
                
                # Tenta encontrar o separador com mais ocorrências na primeira linha
                sep = max(separadores, key=lambda s: primeira_linha.count(s))
                return cod, sep
        except (UnicodeDecodeError, IOError):
            continue
            
    raise ImportacaoError("Não foi possível detectar a codificação ou separador do arquivo.")
