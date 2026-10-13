"""Transforma números e registros em texto para mostrar na tela.

Funções puras: recebem valores e DEVOLVEM uma string (não chamam print()).
Dinheiro chega sempre em centavos (int).
"""

from loja import estoque


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
