"""Guarda e recupera o estado do programa em um arquivo JSON.

É o ÚNICO módulo que abre arquivos. Não imprime nada: devolve avisos como
texto e True/False para quem chamou decidir o que mostrar.
Formato do arquivo: {"produtos": [...], "vendas": [...], "movimentacoes": [...]}
"""

import json
import os

CHAVES_PRODUTO = ["codigo", "nome", "preco_centavos", "saldo"]
CHAVES_VENDA = ["numero", "data", "itens", "total_centavos"]
CHAVES_MOVIMENTACAO = ["data", "tipo", "codigo", "quantidade", "motivo", "saldo_apos"]


def lista_valida(registros, chaves):
    """Devolve True se 'registros' é uma lista de dicionários que têm todas as 'chaves'."""
    if not isinstance(registros, list):
        return False
    for registro in registros:
        if not isinstance(registro, dict):
            return False
        for chave in chaves:
            if chave not in registro:
                return False
    return True


def estrutura_valida(dados):
    """Confere se as três listas do arquivo têm o formato esperado."""
    if not lista_valida(dados.get("produtos", []), CHAVES_PRODUTO):
        return False
    if not lista_valida(dados.get("vendas", []), CHAVES_VENDA):
        return False
    if not lista_valida(dados.get("movimentacoes", []), CHAVES_MOVIMENTACAO):
        return False
    return True


def carregar_json(caminho):
    """Lê um arquivo JSON. Devolve o dicionário lido, ou None se o conteúdo for inválido."""
    dados = None
    try:
        # "utf-8-sig" também aceita arquivos salvos com BOM (ex.: Bloco de Notas)
        with open(caminho, "r", encoding="utf-8-sig") as arquivo:
            dados = json.load(arquivo)
    except ValueError:                    # JSONDecodeError e UnicodeDecodeError são ValueError
        dados = None
    if not isinstance(dados, dict):       # JSON válido com raiz errada (ex.: []) também é inválido
        dados = None
    elif not estrutura_valida(dados):     # JSON válido, mas sem as listas/chaves esperadas
        dados = None
    return dados


def nome_livre_para_copia(caminho):
    """Devolve um nome de cópia que ainda não existe: loja.json.corrompido,
    loja.json.corrompido2, loja.json.corrompido3, ... (nunca apaga uma cópia anterior)."""
    copia = caminho + ".corrompido"
    numero = 2
    while os.path.exists(copia):
        copia = caminho + ".corrompido" + str(numero)
        numero = numero + 1
    return copia


def carregar_dados(caminho, caminho_exemplo):
    """Devolve (produtos, vendas, movimentacoes, aviso). Não imprime: o aviso volta como texto.
    - loja.json ausente: usa o arquivo de exemplo, se existir; senão, listas vazias.
    - loja.json inválido: guarda uma cópia .corrompido e começa com listas vazias."""
    aviso = ""
    dados = {}
    if os.path.exists(caminho):
        lido = carregar_json(caminho)
        if lido is None:
            copia = nome_livre_para_copia(caminho)
            os.replace(caminho, copia)    # preserva o arquivo ruim com outro nome
            aviso = "Arquivo de dados inválido. Cópia guardada em: " + copia
        else:
            dados = lido
    elif os.path.exists(caminho_exemplo):
        lido = carregar_json(caminho_exemplo)
        if lido is not None:              # o exemplo só é lido: nunca é renomeado nem gravado
            dados = lido
            aviso = "Primeira execução: dados de exemplo carregados."
        else:
            aviso = "Arquivo de exemplo inválido: começando sem dados."
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
