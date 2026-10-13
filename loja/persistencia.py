"""Guarda e recupera o estado do programa em um arquivo JSON.

É o ÚNICO módulo que abre arquivos. Não imprime nada: devolve avisos como
texto e True/False para quem chamou decidir o que mostrar.
Formato do arquivo: {"produtos": [...], "vendas": [...], "movimentacoes": [...]}
"""

import json
import os


def carregar_json(caminho):
    """Lê um arquivo JSON. Devolve o dicionário lido, ou None se o conteúdo for inválido."""
    dados = None
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except ValueError:                    # JSONDecodeError e UnicodeDecodeError são ValueError
        dados = None
    if not isinstance(dados, dict):       # JSON válido com raiz errada (ex.: []) também é inválido
        dados = None
    return dados


def carregar_dados(caminho, caminho_exemplo):
    """Devolve (produtos, vendas, movimentacoes, aviso). Não imprime: o aviso volta como texto.
    - loja.json ausente: usa o arquivo de exemplo, se existir; senão, listas vazias.
    - loja.json inválido: guarda uma cópia .corrompido e começa com listas vazias."""
    aviso = ""
    dados = {}
    if os.path.exists(caminho):
        lido = carregar_json(caminho)
        if lido is None:
            copia = caminho + ".corrompido"
            os.replace(caminho, copia)    # preserva o arquivo ruim; nunca o sobrescreve em silêncio
            aviso = "Arquivo de dados inválido. Cópia guardada em: " + copia
        else:
            dados = lido
    elif os.path.exists(caminho_exemplo):
        lido = carregar_json(caminho_exemplo)
        if lido is not None:              # o exemplo só é lido: nunca é renomeado nem gravado
            dados = lido
            aviso = "Primeira execução: dados de exemplo carregados."
    produtos = dados.get("produtos", [])
    vendas = dados.get("vendas", [])
    movimentacoes = dados.get("movimentacoes", [])
    return produtos, vendas, movimentacoes, aviso


def salvar_dados(caminho, produtos, vendas, movimentacoes):
    """Grava todo o estado em JSON legível (UTF-8, acentos sem escape, indentado).
    Retorna: True se salvou; False se o disco recusou (os dados continuam na memória)."""
    dados = {"produtos": produtos, "vendas": vendas, "movimentacoes": movimentacoes}
    texto = json.dumps(dados, ensure_ascii=False, indent=2)   # 1. monta o texto na memória
    temporario = caminho + ".tmp"                              # 2. grava num arquivo temporário
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)  # num clone novo, dados/ pode não existir
        with open(temporario, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
        os.replace(temporario, caminho)                        # 3. troca o arquivo de uma vez
    except OSError:
        return False
    return True
