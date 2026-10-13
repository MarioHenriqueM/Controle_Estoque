"""Transforma números e registros em texto para mostrar na tela.

Funções puras: recebem valores e DEVOLVEM uma string (não chamam print()).
Dinheiro chega sempre em centavos (int).
"""


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
