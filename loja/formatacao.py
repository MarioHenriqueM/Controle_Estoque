"""Transforma números e registros em texto para mostrar na tela.

As funções DEVOLVEM uma string (não chamam print()). Dinheiro chega sempre em
centavos (int). As cores só são usadas quando o terminal é interativo e entende
os códigos de cor ANSI; nos outros casos, o texto sai sem mudança.
"""

import os
import sys

from loja import estoque

# Códigos ANSI: escritos antes do texto, mudam a cor; NORMAL volta ao padrão
VERDE = "\033[32m"
VERMELHO = "\033[31m"
AMARELO = "\033[33m"
CIANO_NEGRITO = "\033[1;36m"
NEGRITO = "\033[1m"
NORMAL = "\033[0m"
LIMPAR_TELA = "\033[2J\033[H"


def suporta_cores(interativo, nome_sistema, ambiente):
    """Decide se o terminal mostra cores. Recebe tudo por parâmetro, para ser testável.
    Fora do Windows, todo terminal interativo aceita cores. No Windows, só o
    Windows Terminal e o terminal do VS Code (o cmd antigo mostraria lixo)."""
    if not interativo or "NO_COLOR" in ambiente:
        return False
    if nome_sistema != "nt":
        return True
    if "WT_SESSION" in ambiente or ambiente.get("TERM_PROGRAM") == "vscode":
        return True
    return False


# Constantes calculadas uma única vez, quando o módulo é carregado (nunca mudam depois)
TERMINAL_INTERATIVO = sys.stdin.isatty() and sys.stdout.isatty()
CORES_ATIVAS = suporta_cores(TERMINAL_INTERATIVO, os.name, os.environ)


def aplicar_cor(texto, codigo, ativo):
    """Devolve o texto entre o código de cor e o código NORMAL.
    Se 'ativo' for False, devolve o texto sem mudança."""
    if not ativo:
        return texto
    return codigo + texto + NORMAL


def sucesso(texto):
    """Texto em verde (operação realizada)."""
    return aplicar_cor(texto, VERDE, CORES_ATIVAS)


def erro(texto):
    """Texto em vermelho (entrada inválida ou operação recusada)."""
    return aplicar_cor(texto, VERMELHO, CORES_ATIVAS)


def aviso(texto):
    """Texto em amarelo (informação importante, sem erro)."""
    return aplicar_cor(texto, AMARELO, CORES_ATIVAS)


def titulo(texto):
    """Texto em ciano e negrito (títulos e cabeçalhos)."""
    return aplicar_cor(texto, CIANO_NEGRITO, CORES_ATIVAS)


def destaque(texto):
    """Texto em negrito (totais)."""
    return aplicar_cor(texto, NEGRITO, CORES_ATIVAS)


def codigo_limpar_tela():
    """Devolve o código que limpa a tela, ou texto vazio se o terminal não o entende."""
    if CORES_ATIVAS:
        return LIMPAR_TELA
    return ""


def formatar_moeda(centavos):
    """Recebe um valor em centavos (int) e devolve o texto 'R$ 1.234,56'."""
    sinal = ""
    if centavos < 0:                 # sinal tratado antes: em Python, -150 // 100 == -2
        sinal = "-"
        centavos = -centavos
    reais = centavos // 100
    resto = centavos % 100
    reais_texto = f"{reais:,}".replace(",", ".")    # 1,234 -> 1.234
    return f"{sinal}R$ {reais_texto},{resto:02d}"


def cabecalho_produtos():
    """Devolve o cabeçalho da tabela de produtos."""
    codigo = "Código"
    nome = "Nome"
    preco = "Preço"
    saldo = "Saldo"
    titulo = f"{codigo:>6}  {nome:<30}  {preco:>14}  {saldo:>7}"
    return titulo + "\n" + "-" * len(titulo)


def linha_produto(produto):
    """Devolve uma linha da tabela de produtos, com as colunas alinhadas."""
    codigo = produto["codigo"]
    nome = produto["nome"]
    preco = formatar_moeda(produto["preco_centavos"])
    saldo = produto["saldo"]
    return f"{codigo:>6}  {nome:<30}  {preco:>14}  {saldo:>7}"


def cabecalho_extrato():
    """Devolve o cabeçalho da tabela de movimentações (extrato)."""
    data = "Data"
    tipo = "Tipo"
    quantidade = "Qtd"
    motivo = "Motivo"
    saldo = "Saldo após"
    titulo = f"{data:<16}  {tipo:<8}  {quantidade:>7}  {motivo:<14}  {saldo:>10}"
    return titulo + "\n" + "-" * len(titulo)


def linha_extrato(movimentacao):
    """Devolve uma linha do extrato: entradas com '+' e saídas/vendas com '-'."""
    data = movimentacao["data"]
    tipo = movimentacao["tipo"]
    motivo = movimentacao["motivo"]
    saldo = movimentacao["saldo_apos"]
    if tipo == estoque.TIPO_ENTRADA:
        quantidade = "+" + str(movimentacao["quantidade"])
    else:
        quantidade = "-" + str(movimentacao["quantidade"])
    return f"{data:<16}  {tipo:<8}  {quantidade:>7}  {motivo:<14}  {saldo:>10}"


def linha_item(item):
    """Devolve a linha de um item de venda: quantidade x nome, preço unitário e subtotal."""
    codigo = item["codigo"]
    quantidade = item["quantidade"]
    nome = item["nome"]
    preco = formatar_moeda(item["preco_unitario_centavos"])
    subtotal = formatar_moeda(item["subtotal_centavos"])
    return f"{codigo:>6}  {quantidade:>5} x {nome:<30}  {preco:>14}  {subtotal:>14}"
